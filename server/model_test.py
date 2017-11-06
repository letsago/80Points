import unittest
from model import *

class TestCard(unittest.TestCase):
	def testSorted(self):
		tests = [
			([Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     [Card('h', '3'), Card('s', 'A'), Card('joker', 'big')]),
			([Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
			([Card('d', '8'), Card('c', 'K'), Card('h', '3')],
		     [Card('c', 'K'), Card('d', '8'), Card('h', '3')]),
		    ([Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
		    ([Card('c', 'K'), Card('c', '2'), Card('c', '10')],
		     [Card('c', '2'), Card('c', '10'), Card('c', 'K')])		     			
		]
		        
		for test in tests:
			test_list, want = test
			self.assertEqual(sorted(test_list), want)
	
	def testIsTrump(self):
		tests = [
			('h','2', Card('s','3'), False),
			('h','2', Card('h','3'), True),
			('h','2', Card('s','2'), True),
		]

		for test in tests:
			suit, value, card, want = test
			self.assertEqual(card.isTrump(suit, value), want)

	def testTrumpSort(self):
		tests = [
			('s', '3',
			 [Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     [Card('s', 'A'), Card('h', '3'), Card('joker', 'big')]),
			('s', '3',
			 [Card('joker', 'big'), Card('s', 'A'), Card('s', '3'), Card('h', '3')],
		     [Card('s', 'A'), Card('h', '3'), Card('s', '3'), Card('joker', 'big')]),
			('s', '2',
			 [Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
			('c', '3',
			 [Card('c', 'K'), Card('d', '8'), Card('h', '3')],
		     [Card('d', '8'), Card('c', 'K'), Card('h', '3')]),
		    ('h', '3',
		     [Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     [Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]),
		    ('d', '2',
		     [Card('c', 'K'), Card('c', '2'), Card('c', '10')],
		     [Card('c', '10'), Card('c', 'K'), Card('c', '2')])
		]
		for test in tests:
			trump_suit, trump_value, test_list, want = test
			self.assertEqual(trumpSorted(test_list, trump_suit, trump_value), want)

if __name__ == '__main__':
	unittest.main()