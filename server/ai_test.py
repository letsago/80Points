import ai
import model
import test_utils
import tractor
import unittest

class TestGetSplits(unittest.TestCase):
	def setUp(self):
		self.trick_suit = 's'
		self.trump_card = model.Card('h', '2')

	def check(self, test):
		large, small = test_utils.apply_cards_from_str(test['large'], test['small'])
		large_tractor = tractor.cards_to_tractors(large, self.trick_suit, self.trump_card)[0]
		small_tractor = tractor.cards_to_tractors(small, self.trick_suit, self.trump_card)[0]
		splits = ai.get_splits(large_tractor, small_tractor)
		self.assertEqual(len(splits), len(test['splits']))
		for i, split in enumerate(splits):
			expected_cards = test_utils.cards_from_str(test['splits'][i])
			expected_tractor = tractor.cards_to_tractors(expected_cards, self.trick_suit, self.trump_card)[0]
			self.assertEqual(split, expected_tractor)
			self.assertEqual(ai.flatten(split.orig_cards), expected_cards)

	def testComplexSplit(self):
		test = {
			'large': '3s 3s 3s 4s 4s 4s 5s 5s 5s',
			'small': '8s 8s 9s 9s',
			'splits': [
				'3s 3s 4s 4s',
				'4s 4s 5s 5s',
			],
		}
		self.check(test)

if __name__ == '__main__':
	unittest.main()
