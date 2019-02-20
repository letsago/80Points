import unittest
import mock
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
			self.assertEqual(card.is_trump(suit, value), want)

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
			self.assertEqual(trump_sorted(test_list, trump_suit, trump_value), want)

class TestRound(unittest.TestCase):
	def testFirstPlayerSetToBottomPlayer(self):
		num_players = 4
		num_decks = 2
		first_player = 0
		third_player = 2
		# Mock model.create_random_deck to use a determinstic deck.
		with mock.patch('model.create_random_deck', return_value=create_deck(num_decks)):
			round = Round(num_players)
		self.assertEqual(round.state.turn, first_player)
		# Deal out all cards.
		for _ in range(len(round.state.deck)):
			round.tick()
		# After dealing out all cards, the turn should return to the first player.
		self.assertEqual(round.state.turn, first_player)
		# Have the third player declare the 2 of hearts.
		round.declare(third_player, [Card('h', '2')])
		# This tick allows for the player to receive the bottom cards.
		round.tick()
		round.set_bottom(third_player, 
			[Card('c', '4'), Card('c', '6'), Card('c', '8'), Card('c', 'Q'),
			 Card('d', '3'), Card('d', '5'), Card('d', '7'), Card('d', '9')])
		# After setting the bottom, it should now be the third player's turn.
		self.assertEqual(round.state.turn, third_player)


if __name__ == '__main__':
	unittest.main()