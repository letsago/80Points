import unittest
import mock
from model import *
from parameterized import parameterized

class TestCard(unittest.TestCase):
	def testIsTrump(self):
		tests = [
			(Card('h','2'), Card('s','3'), False),
			(Card('h','2'), Card('h','3'), True),
			(Card('h','2'), Card('s','2'), True),
		]

		for test in tests:
			trump_card, card, want = test
			self.assertEqual(card.is_trump(trump_card), want)

	def testDisplaySorted(self):
		tests = [
			(
				Card('joker', '2'),
				[Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     	[Card('h', '3'), Card('s', 'A'), Card('joker', 'big')]
			),

			(	
				Card('joker', '2'),
				[Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

			(
				Card('joker', '2'),
				[Card('d', '8'), Card('c', 'K'), Card('h', '3')],
		     	[Card('c', 'K'), Card('d', '8'), Card('h', '3')]
			),

		    	(
			    	Card('joker', '2'),
			    	[Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

		    	(
			    	Card('joker', '2'),
			    	[Card('c', 'K'), Card('c', '3'), Card('c', '10')],
		     	[Card('c', '3'), Card('c', '10'), Card('c', 'K')]
			),

		    	(
				Card('joker', '2'),
				[Card('c', '2'), Card('d', '2'), Card('c', '2')],
		     	[Card('c', '2'), Card('c', '2'), Card('d', '2')]
			),

			(
				Card('s', '3'),
			 	[Card('joker', 'big'), Card('s', 'A'), Card('h', '3')],
		     	[Card('s', 'A'), Card('h', '3'), Card('joker', 'big')]
			),

			(	
				Card('s', '3'),
				[Card('joker', 'big'), Card('s', 'A'), Card('s', '3'), Card('h', '3')],
		     	[Card('s', 'A'), Card('h', '3'), Card('s', '3'), Card('joker', 'big')]
			),

			(	
				Card('s', '2'),
				[Card('joker', 'small'), Card('joker', 'big'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

			(
				Card('c', '3'),
				[Card('c', 'K'), Card('d', '8'), Card('h', '3')],
		     	[Card('d', '8'), Card('c', 'K'), Card('h', '3')]
			),

		    	(
				Card('h', '3'),
		     	[Card('joker', 'big'), Card('joker', 'small'), Card('h', '3')],
		     	[Card('h', '3'), Card('joker', 'small'), Card('joker', 'big')]
			),

		    	(
				Card('d', '2'),
		     	[Card('c', 'K'), Card('c', '2'), Card('c', '10')],
		     	[Card('c', '10'), Card('c', 'K'), Card('c', '2')]
			)
		]
		for test in tests:
			trump_card, test_list, want = test
			self.assertEqual(display_sorted(test_list, trump_card), want)

class TestRound(unittest.TestCase):
	def testFirstPlayerSetToBottomPlayer(self):
		num_players = 4
		num_decks = 2
		first_player = 0
		third_player = 2
		# Mock model.create_random_deck to use a deterministic deck.
		with mock.patch('model.create_random_deck', return_value=create_deck(num_decks)):
			round = Round(num_players)
		self.assertEqual(round.state.turn, first_player)
		# Deal out all cards.
		for _ in range(len(round.state.deck)):
			round.tick()
		# After dealing out all cards, the turn should return to the first player.
		self.assertEqual(round.state.turn, first_player)
		# Have the third player declare the 2 of diamonds.
		round.declare(third_player, [Card('d', '2')])
		# This tick allows for the player to receive the bottom cards.
		round.tick()
		# After getting the bottom, it should now be the third player's turn.
		self.assertEqual(round.state.turn, third_player)
		round.set_bottom(third_player, 
			[Card('d', '4'), Card('d', '6'), Card('d', '8'), Card('d', '10'),
			 Card('c', '3'), Card('c', '5'), Card('c', '7'), Card('c', '9')])
		# After the bottom is set, it should still be the third player's turn.
		self.assertEqual(round.state.turn, third_player)

class TestRoundState(unittest.TestCase):
	def setUp(self):
		self.num_players = 4
		self.round_state = RoundState(self.num_players)
		self.round_state.trump_card = Card('c', '3')

	@parameterized.expand([
		['no play', []],

		['different suits 2 singles', [Card('d', '2'), Card('h', '3')]],

		['different suits 1 pair + 1 single', [Card('d', '2'), Card('d', '2'), Card('s', '5')]],

		['same suits 2 nonconsecutive pairs', [Card('h', '2'), Card('h', '2'), Card('h', '6'), Card('h', '6')]],

		['different suits 2 consecutive pairs + single', 
			[Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5'), Card('c', '5')]],

		['different suits 2 nonconsecutive pairs', 
			[Card('d', '4'), Card('d', '4'), Card('h', '5'), Card('h', '5')]],
			
		['different suits 2 consecutive pairs + pair', 
			[Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5'), Card('s', '7'), Card('s', '7')]],
	])

	def testInvalidFirstPlays(self, name, play):
		self.assertFalse(self.round_state.is_play_valid(play))
	
	@parameterized.expand([
		['1 single', [Card('h', '2')]],

		['same suit 1 pair', [Card('s', '2'), Card('s', '2')]],

		['same suit 2 consecutive pairs considering trump value', 
			[Card('c', '2'), Card('c', '2'), Card('c', '4'), Card('c', '4')]],

		['same suit 2 consecutive pairs', 
			[Card('c', '4'), Card('c', '4'), Card('c', '5'), Card('c', '5')]],

		['same suit 3 consecutive pairs considering trump value', 
			[Card('d', '2'), Card('d', '2'), Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5')]],

		['same suit 3 consecutive pairs', 
			[Card('d', '4'), Card('d', '4'), Card('d', '5'), Card('d', '5'), Card('d', '6'), Card('d', '6')]],
	])

	def testValidFirstPlays(self, name, play):
		self.assertTrue(self.round_state.is_play_valid(play))

	@parameterized.expand([
		['no play', 0, [], []],

		['too many cards', 0, [Card('s', '3'), Card('s', '3'), Card('s', '4')], []],

		['cards not in player hand', 0, [Card('h', '3')], []],

		['card value does not match trump value', 0, [Card('s', '4')], []],

		['cards do not have the same suit', 0, [Card('s', '3'), Card('d', '3')], []],

		['equal length to most recent declaration', 0, [Card('s', '3')], 
			[Declaration(1, [Card('d', '3')])]],

		['smaller length than most recent declaration', 0, [Card('s', '3')], 
			[Declaration(1, [Card('d', '3')]), Declaration(1, [Card('d', '3'), Card('d', '3')])]],

		['suit does not match previous declaration', 0, [Card('s', '3'), Card('s', '3')], 
			[Declaration(0, [Card('d', '3')])]],
	])

	def testInvalidDeclarations(self, name, player, cards, declarations):
		self.round_state.declarations = declarations
		self.round_state.player_hands[0] = [Card('s', '4'), Card('s', '3'), Card('s', '3'), Card('d', '3')]
		self.assertFalse(self.round_state.is_declaration_valid(player, cards))

	@parameterized.expand([
		['initial play', 0, [Card('s', '3')], []],

		['overturn another declaration', 0, [Card('s', '3'), Card('s', '3')], 
			[Declaration(1, [Card('d', '3')])]],

		['defend previous declaration', 0, [Card('s', '3'), Card('s', '3')], 
			[Declaration(0, [Card('s', '3')])]],
	])

	def testValidDeclarations(self, name, player, cards, declarations):
		self.round_state.declarations = declarations
		self.round_state.player_hands[0] = [Card('s', '4'), Card('s', '3'), Card('s', '3'), Card('d', '3')]
		self.assertTrue(self.round_state.is_declaration_valid(player, cards))

if __name__ == '__main__':
	unittest.main()