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
		suits: ['Clubs', 'Diamonds', 'Hearts', 'Spades'],
		ranks: ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
		players: [],
	}
})


socket.emit('join', 'player');

socket.on('lobby', function (data) {
	app.players = data;
});