var socket = io();

// A card component
Vue.component('card', {
	props: ['suit', 'rank', 'selected', 'selectable', 'trumpSuit', 'trumpRank'],
	template: '#card-template',
	computed: {
		isTrump: function() {
			if (this.suit == 'joker') {
				return true;
			}
			return (this.suit == this.trumpSuit || this.rank == this.trumpRank);
		},
		rankClass: function () {
			if (this.rank == 'big' || this.rank == 'small') {
				return this.rank;
			}
			return 'rank-' + this.rank.toLowerCase();
		},
		rankDisplay: function () {
			if (this.rank == 'big' || this.rank == 'small') {
				return '-';
			}
			return this.rank;
		},
		suitClass: function() {
			const classes = {
				c: 'clubs',
				d: 'diams',
				h: 'hearts',
				s: 'spades',
				joker: 'joker',
			}
			return classes[this.suit];
		},
		suitDisplay: function() {
			if (this.suit == 'joker') {
				return 'Joker';
			}
			return '&' + this.suitClass + ';';
		},
		classObj: function() {
			let c = {
				card: true,
				trump: this.isTrump && !this.selected,
				selected: this.selected,
			};
			c[this.rankClass] = true;
			c[this.suitClass] = true;
			return c;
		},
	},
	methods: {
		toggleSelected: function() {
			// Don't allow selecting when the card is not selectable, but do allow for it to be de-selected.
			if (!this.selected && !this.selectable) {
				return;
			}
			this.$emit('update-selected', !this.selected);
		},
	},
})

// Main Vue instance
var app = new Vue({
	el: '#app',
	data: {
		debug: false,
		mode: 'register',

		playerName: '',

		gameList: [],
		createGameOptions: {
			name: '',
			numPlayers: 4,
		},

		status: 'disconnected',
		game_id: null,
		player: -1,
		cards: [],
		trumpSuit: '',
		trumpRank: '2',
		turn: -1,
		bottomSize: -1,
		suits: {
			'c': 'Clubs',
			'd': 'Diamonds',
			'h': 'Hearts',
			's': 'Spades',
		},
		ranks: ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
		playerPositions: ['bottomPlayer', 'leftPlayer', 'topPlayer', 'rightPlayer'],
		players: [],
		declaration: null,
		declarableSuits: {},
		board: [],
	},
	computed: {
		selectedCards: function() {
			return this.cards.filter(card => {
				return card.selected;
			});
		},
		canSetBottom: function () {
			return this.status == 'bottom' && this.player == this.declaration.player;
		},
		canPlay: function () {
			return this.status == 'playing' && this.player == this.turn;
		},
		canSelectNewCards: function() {
			return !(this.canSetBottom && this.selectedCards.length >= this.bottomSize);
		},
		isObserver: function() {
			return this.player == null;
		},
	},
	methods: {
		register: function(name) {
			socket.emit('register', name);
		},
		createGame: function(name, numPlayers) {
			socket.emit('create', name, numPlayers);
		},
		refreshGameList: function() {
			socket.emit('game_list');
		},
		joinGame: function(gameId) {
			socket.emit('join', gameId);
		},
		joinGameAs: function(gameId, playerIdx) {
			socket.emit('join_as', gameId, playerIdx);
		},
		clearSelectedCards: function() {
			app.cards.forEach(function(el) {
				el.selected = false;
			});
		},
		declareSuit: function (suit) {
			// find all cards matching trumpRank in this suit, and declare them together
			let cards = this.cards.filter(card => {
				return (card.suit == suit && card.value == this.trumpRank);
			});
			socket.emit('round_declare', cards);
		},
		setBottom: function () {
			socket.emit('round_set_bottom', this.selectedCards);
			clearSelectedCards();
		},
		play: function () {
			socket.emit('round_play', this.selectedCards);
			clearSelectedCards();
		},
		playerPosition: function(index) {
			// This function assigns the right CSS class so that the person who
			// is playing is always on the bottom of the table.
			//
			// 'index' is in the order in which players joined the game, i.e.
			// 0 is the first person who joined.
			// 'this.player' is the current player's index.
			//
			// When 'index' == 'this.player', this expression is 0, which maps
			// to the bottom player's position in 'this.playerPositions'.
			// Even though the elements are always listed with index 0 first
			// in the HTML, the CSS grid ignores order of the element and goes
			// strictly based on the CSS class.
			var bottomIndex = this.player;
			if(bottomIndex === null) {
				// observer, put arbitrary player at the bottom
				bottomIndex = 0;
			}
			return this.playerPositions[(index - bottomIndex + 4) % 4];
		},
	},
})

function mergeCards(oldCards, newCards) {
	let merged = [];
	newCards.forEach(function(card) {
		// If we see the new card in the old hand, we push the old element onto the merged
		// hand to preserve selected status.
		for (let i = 0; i < oldCards.length; i++) {
			if (oldCards[i].suit == card.suit && oldCards[i].value == card.value) {
				merged.push(oldCards[i]);
				oldCards.splice(i, 1);
				return;
			}
		}
		merged.push({
			suit: card.suit,
			value: card.value,
			// Needs default value for selected.
			selected: false,
		});
	});
	return merged;
}

socket.on('debug', function(data) {
	app.debug = true;
});

socket.on('register', function(name) {
	app.playerName = name;
	app.mode = 'list';
	app.refreshGameList();
});

socket.on('game_list', function(data) {
	console.log('received ' + data);
	app.gameList = data;
});

socket.on('lobby', function (data) {
	app.mode = 'game';
	app.game_id = data.game_id;
	app.players = data.players;
	app.player = data.playerIndex;
});

socket.on('state', function(data) {
	app.status = data.status;
	app.player = data.player;
	app.trumpSuit = data.trump_suit;
	app.trumpRank = data.trump_value;
	app.turn = data.turn;
	app.declaration = data.declaration;
	app.board = data.board;
	app.bottomSize = data.bottom_size;

	app.cards = mergeCards(app.cards, data.hand);

	// set declarable suits
	// TODO: make this computed?
	if (data.status == 'dealing') {
		var numCardsNeeded = 1;
		if (data.declaration) {
			numCardsNeeded = data.declaration.cards.length + 1;
		}
		var numTrumpInSuits = {};
		data.hand.forEach(function(el) {
			if (el.value == data.trump_value) {
				if (el.suit in numTrumpInSuits) {
					numTrumpInSuits[el.suit]++;
				} else {
					numTrumpInSuits[el.suit] = 1;
				}
			}
		});
		declarableSuits = {};
		for(var suit in numTrumpInSuits) {
			if (numTrumpInSuits[suit] >= numCardsNeeded) {
				declarableSuits[suit] = true;
			}
		}
		app.declarableSuits = declarableSuits;
	} else {
		app.declarableSuits = {};
	}
});
