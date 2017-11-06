var socket = io();

// A card component
Vue.component('card', {
	props: ['suit', 'rank', 'selected', 'trumpSuit', 'trumpRank'],
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
			this.$emit('update-selected', !this.selected);
		},
	},
})

// Main Vue instance
var app = new Vue({
	el: '#app',
	data: {
		status: 'disconnected',
		player: -1,
		cards: [
			{suit: 'h', value: 'A', selected: false},
			{suit: 'd', value: '2', selected: false},
			{suit: 's', value: '3', selected: false},
			{suit: 'c', value: '10', selected: false},
			{suit: 'c', value: 'K', selected: false},
			{suit: 'joker', value: 'big', selected: false},
			{suit: 'joker', value: 'small', selected: false},
		],
		trumpSuit: 'c',
		trumpRank: '2',
		turn: -1,
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
	},
	computed: {
		canSetBottom: function () {
			return this.status == 'bottom' && this.player == this.declaration.player;
		},
	},
	methods: {
		declareSuit: function (suit) {
			// find all cards matching trumpRank in this suit, and declare them together
			var cards = [];
			var trumpRank = this.trumpRank;
			this.cards.forEach(function(card) {
				if (card.suit == suit && card.value == trumpRank) {
					cards.push(card);
				}
			});
			socket.emit('round_declare', cards);
		},
		setBottom: function () {
			var cards = [];
			this.cards.forEach(function(card) {
				if (card.selected) {
					cards.push(card);
				}
			});
			socket.emit('round_set_bottom', cards);
		},
	},
})


socket.emit('join', 'player');

socket.on('lobby', function (data) {
	app.players = data;
});

socket.on('state', function(data) {
	app.status = data.status;
	app.player = data.player;
	app.trumpSuit = data.trump_suit;
	app.trumpRank = data.trump_value;
	app.turn = data.turn;
	app.declaration = data.declaration;

	app.cards = data.hand.map(function(el) {
		return {
			suit: el.suit,
			value: el.value,
			selected: false,
		};
	});

	// set declarable suits
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
