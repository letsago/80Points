// A card component
Vue.component('card', {
	props: ['suit', 'value'],
	template: '#card-template',
	computed: {
		rankClass: function () {
			if (this.value == 'big' || this.value == 'small') {
				return this.value;
			}
			return 'rank-' + this.value.toLowerCase();
		},
		rankDisplay: function () {
			if (this.value == 'big' || this.value == 'small') {
				return '-';
			}
			return this.value;
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
			};
			c[this.rankClass] = true;
			c[this.suitClass] = true;
			return c;
		},
	},
})

// Main Vue instance
var app = new Vue({
	el: '#app',
	data: {
		cards: [
			{suit: 'h', value: 'A'},
			{suit: 'd', value: '2'},
			{suit: 's', value: '3'},
			{suit: 'c', value: 'K'},
			{suit: 'joker', value: 'big'},
			{suit: 'joker', value: 'small'},
		],
	}
})