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
]