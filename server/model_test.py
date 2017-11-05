import unittest
from model import Card

class TestModel(unittest.TestCase):
	def testCardSorted(self):
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
			self.assertEqual(sorted(test[0]), test[1])
		

if __name__ == '__main__':
	unittest.main()