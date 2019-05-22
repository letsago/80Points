from model import Card
from tractor_test import Double, Straight
from tractor import SUIT_LOWEST, SUIT_TRICK, SUIT_TRUMP

cards_to_tractors_test_data = [
		(
			"same suit consecutive pairs",
			Double('s', '2') + Double('s', '3'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP}],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"same suit consecutive singles",
			Straight('s', '2', 4),
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"different suit consecutive value singles",
			[Card('s', '2'), Card('d', '3')],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"single",
			[Card('s', '2')],
			[{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST}],
		),

		(
			"same suit consecutive pairs and single",
			Double('s', '2') + Double('s', '3') + [Card('s', '5')],
			[
				{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"different suit pair and single",
			Double('s', '2') + [Card('d', '3')],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"same suit 3 consecutive pairs",
			Double('s', '2') + Double('s', '3') + Double('s', '4'),
			[{'rank': 2, 'length': 3, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP}],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"same suit 3 non-consecutive pairs",
			Double('s', '2') + Double('s', '5') + Double('s', '9'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"same suit 2 consecutive pairs, 1 separate pair, 1 single",
			Double('s', '2') + Double('s', '3') + Double('s', '9') + [Card('joker', 'big')],
			[
				{'rank': 2, 'length': 2, 'power_card': Card('s', '2'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('joker', 'big'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('joker', 'big'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"consecutive joker pair",
			Double('joker', 'big') + Double('joker', 'small'),
			[{'rank': 2, 'length': 2, 'power_card': Card('joker', 'small'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('joker', 'small'), 'suit_type': SUIT_TRUMP}],
		),

		(
			"consecutive trump value, joker pair",
			Double('s', '8') + Double('joker', 'small'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
		),

		(
			"trump suit 2 non-consecutive pairs",
			Double('c', '8') + Double('h', '8'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
		),

		(
			"different suit 2 consecutive value pairs",
			Double('c', '2') + Double('h', '3'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '2'), 'suit_type': SUIT_TRICK},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '2'), 'suit_type': SUIT_TRICK},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"different suit 2 non-consecutive value pairs",
			Double('h', '2') + Double('d', '5'),
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '5'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"different suit 2 nonconsecutive trump value pairs",
			Double('c', '8') + Double('h', '8'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
			],
		),

		(
			"trump value, joker 2 consecutive pairs",
			Double('s', '8') + Double('joker', 'small'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
			[{'rank': 2, 'length': 2, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP}],
		),

		(
			"same suit 2 consecutive pairs due to trump value",
			Double('h', '7') + Double('h', '9'),
			[
				{'rank': 1, 'length': 1, 'power_card': Card('h', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '7'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '7'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('h', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '9'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '7'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '7'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"s 8 trump - trump value 2 consecutive pairs; joker 8 trump - trump value 2 nonconsecutive pairs",
			Double('s', '8') + Double('d', '8'),
			[{'rank': 2, 'length': 2, 'power_card': Card('d', '8'), 'suit_type': SUIT_TRUMP}],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('s', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('d', '8'), 'suit_type': SUIT_TRUMP},
			],
		),

		(
			"s 8 trump - trump suit, trump value 2 consecutive pairs; joker 8 trump - different suit 2 nonconsecutive pairs",
			Double('s', 'A') + Double('h', '8'),
			[{'rank': 2, 'length': 2, 'power_card': Card('s', 'A'), 'suit_type': SUIT_TRUMP}],
			[
				{'rank': 2, 'length': 1, 'power_card': Card('h', '8'), 'suit_type': SUIT_TRUMP},
				{'rank': 1, 'length': 1, 'power_card': Card('s', 'A'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('s', 'A'), 'suit_type': SUIT_LOWEST},
			],
		),

		(
			"s 8 trump - trump value, joker 2 nonconsecutive pairs; joker 8 trump - trump value, joker 2 consecutive pairs",
			Double('c', '8') + Double('joker', 'small'),
			[
				{'rank': 2, 'length': 1, 'power_card': Card('joker', 'small'), 'suit_type': SUIT_TRUMP},
				{'rank': 2, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
			],
			[{'rank': 2, 'length': 2, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP}],
		),

		(	"different lowest suit consecutive value pairs",
			Double('h', '2') + Double('d', '3'),
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
			],
			[
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('d', '3'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
				{'rank': 1, 'length': 1, 'power_card': Card('h', '2'), 'suit_type': SUIT_LOWEST},
			],
		),
]
