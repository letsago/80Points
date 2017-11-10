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
		joined: false,
		playerName: '',
		status: 'disconnected',
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
	},
	methods: {
		declareSuit: function (suit) {
			// find all cards matching trumpRank in this suit, and declare them together
			let cards = this.cards.filter(card => {
				return (card.suit == suit && card.value == this.trumpRank);
			});
			socket.emit('round_declare', cards);
		},
		joinAs: function(playerName) {
			socket.emit('join', playerName);
			this.joined = true;
			this.playerName = playerName;
		},
		setBottom: function () {
			socket.emit('round_set_bottom', this.selectedCards);
		},
		play: function () {
			socket.emit('round_play', this.selectedCards);
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

socket.on('connect', () => {
	socket.emit('players');
});

socket.on('lobby', function (data) {
	app.players = data;
	if (!app.joined && app.playerName == '' && app.players.length < 4) {
		let num = app.players.length + 1;
		app.playerName = 'player' + num.toString();
	}
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
