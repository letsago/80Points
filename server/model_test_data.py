from model import Card

follow_suit_validity_test_data = [
    [
        'can play any cards if out of suit but number of cards must be equal',
        [Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5')],
        [Card('s', '4'), Card('c', '3'), Card('c', '3')],
        [Card('h', '5'), Card('s', '4'), Card('c', '3'), Card('c', '3')]
    ],

    [
        'single - must follow trick suit',
        [Card('s', '4')],
        [Card('h', '5')],
        [Card('s', '5')]
    ],

    [
        'pair - must follow trick suit',
        [Card('s', '2'), Card('s', '2')],
        [Card('s', '4'), Card('s', '5')],
        [Card('s', '5'), Card('s', '5')]
    ],

    [
        '2 consecutive pairs - must follow trick suit',
        [Card('c', '4'), Card('c', '4'), Card('c', '5'), Card('c', '5')],
        [Card('h', '3'), Card('s', '3'), Card('s', '3'), Card('joker', 'small')],
        [Card('s', '3'), Card('s', '3'), Card('c', '3'), Card('c', '3')]
    ],

    [
        'pair forces out last single so must play that single',
        [Card('h', '2'), Card('h', '2')],
        [Card('s', '3'), Card('s', '3')],
        [Card('h', '5'), Card('s', '4')]
    ],

    [
        '2 consecutive pairs forces out last single so must play that single',
        [Card('h', '4'), Card('h', '4'), Card('h', '5'), Card('h', '5')],
        [Card('s', '3'), Card('s', '3'), Card('c', '3'), Card('c', '3')],
        [Card('h', '5'), Card('s', '4'), Card('s', '5'), Card('s', '5')]
    ],

    [
        '2 consecutive pairs forces out same suit pairs so must play those pairs',
        [Card('s', '6'), Card('s', '6'), Card('s', '7'), Card('s', '7')],
        [Card('s', '5'), Card('s', '4'), Card('s', '10'), Card('s', 'K')],
        [Card('s', '5'), Card('s', '5'), Card('s', '10'), Card('s', 'K')]
    ],

    [
        'consecutive pair of triples forces out individual triples before consecutive pair of doubles',
        [Card('c', '6'), Card('c', '6'), Card('c', '6'), Card('c', '7'), Card('c', '7'), Card('c', '7')],
        [Card('s', '3'), Card('s', '3'), Card('c', '3'), Card('c', '3'), Card('c', '8'), Card('c', '8')],
        [Card('c', '8'), Card('c', '8'), Card('c', '8'), Card('s', '3'), Card('s', '3'), Card('h', '3')]
    ],

    [
        'must break in-hand 2 consecutive pairs if no other pairs',
        [Card('d', '3'), Card('d', '3')],
        [Card('h', '3'), Card('joker', 'small')],
        [Card('s', '3'), Card('s', '3')]
    ],

    [
        'must break longer length tractor if shorter length, same rank tractor is played',
        [Card('c', '6'), Card('c', '6'), Card('c', '7'), Card('c', '7')],
        [Card('c', '8'), Card('c', '8'), Card('s', '3'), Card('s', '3')],
        [Card('c', '3'), Card('c', '3'), Card('joker', 'small'), Card('joker', 'small')]
    ],

    [
        'flush of 3 singles - must match suit',
        [Card('s', 'A'), Card('s', 'K'), Card('s', 'Q')],
        [Card('s', '5'), Card('s', '5'), Card('h', '5')],
        [Card('s', '4'), Card('s', '5'), Card('s', 'K')],
    ],
]

follow_suit_validity_custom_hand_test_data = [
    [
        'flush of 2 consecutive pairs and one double - must play tractor',
        '10s 10s Ks Ks As As',
        '2s 2s 5s 5s 7s 7s 8s 8s',
        '7s 7s 2s 2s 5s 5s',
        '5s 5s 7s 7s 8s 8s',
    ],

    [
        'flush of 2 tractors, each a 2-length consecutive pair, and player plays one 4-length tractor',
        '10s 10s Js Js Ks Ks As As',
        '6s 6s 7s 7s 8s 8s 9s 9s',
        None,
        '6s 6s 7s 7s 8s 8s 9s 9s',
    ],

    [
        'flush of triple and single, player must play at least one pair',
        '10s 10s 10s Js',
        '6s 6s 7s 7s 8s 9s',
        '6s 7s 8s 9s',
        '6s 6s 7s 7s',
    ],

    [
        'flush of triple and pair, player must play 2 pairs',
        '10s 10s 10s Js Js',
        '6s 6s 7s 7s 8s 9s 9s',
        '6s 6s 7s 8s 9s',
        '6s 6s 7s 7s 9s',
    ],
]

failed_flush_tests = [
    [
        'flush of 2-length consecutive pair + single, player must play 2-length consecutive pair',
        '10s 10s Js Js 10s',
        '6s 6s 7s 7s 9s 9s',
        '6s 6s 7s 9s 9s',
        '6s 6s 7s 7s 9s',
    ],

    [
        'flush of triple and 2-length consecutive pair, player must play 2-length consecutive pair and pair',
        '10s 10s 10s Qs Qs Ks Ks',
        '6s 6s 7s 7s 8s 8s 9s 9s Js',
        '6s 6s 7s 8s 8s 9s Js',
        '6s 6s 7s 7s 9s 9s Js',
    ],
]
