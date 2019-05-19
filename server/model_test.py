import unittest
import mock
from model import *
from parameterized import parameterized
import model_test_data
from tractor_test import tractor_generator
from tractor import SUIT_LOWEST, SUIT_TRICK, SUIT_TRUMP
import test_utils

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
	def setUp(self):
		self.num_players = 4
		self.num_decks = 2
		self.first_player = 0
		self.third_player = 2
		self.full_hand_size = 25
		bottom_size = 8
		self.full_hand_with_bottom_size = self.full_hand_size + bottom_size
		self.declaration_bottom_cards = [
			Card('joker', 'big'), Card('joker', 'big'), Card('joker', 'small'), Card('joker', 'small'),
			Card('d', 'A'), Card('h', 'A'), Card('s', 'A'), Card('c', 'A')
		]

	def testFirstPlayerSetToBottomPlayer(self):
		# Mock model.create_random_deck to use a deterministic deck.
		with mock.patch('model.create_random_deck', return_value=create_deck(self.num_decks)):
			round = Round(self.num_players)
		self.assertEqual(round.state.turn, self.first_player)
		# Deal out all cards.
		for _ in range(len(round.state.deck)):
			round.deal_card()
		# After dealing out all cards, the turn should return to the first player.
		self.assertEqual(round.state.turn, self.first_player)
		# Have the third player declare the 2 of diamonds.
		round.declare(self.third_player, [Card('d', '2')])
		round.finalize_declaration()
		# After getting the bottom, it should now be the third player's turn.
		self.assertEqual(round.state.turn, self.third_player)
		round.set_bottom(self.third_player,
			[Card('d', '4'), Card('d', '6'), Card('d', '8'), Card('d', '10'),
			 Card('c', '3'), Card('c', '5'), Card('c', '7'), Card('c', '9')])
		# After the bottom is set, it should still be the third player's turn.
		self.assertEqual(round.state.turn, self.third_player)

	def testCreateDeckFromFile(self):
		round = Round(self.num_players, deck_name='declaration')
		# Deal out all cards.
		for _ in range(len(round.state.deck)):
			round.deal_card()
		# Verify the first few cards in each hand.
		self.assertEqual(round.state.player_hands[0][:3],
			[Card('d', '2'), Card('d', '3'), Card('d', '4')])
		self.assertEqual(round.state.player_hands[1][:3],
			[Card('h', '2'), Card('h', '2'), Card('h', '3')])
		self.assertEqual(round.state.player_hands[2][:3],
			[Card('s', '2'), Card('s', '2'), Card('s', '3')])
		self.assertEqual(round.state.player_hands[3][:3],
			[Card('c', '2'), Card('c', '2'), Card('c', '3')])
		# Verify the bottom is set properly.
		self.assertEqual(round.state.bottom,
			[Card('c', 'A'), Card('s', 'A'), Card('h', 'A'), Card('d', 'A'),
			 Card('joker', 'small'), Card('joker', 'small'), Card('joker', 'big'), Card('joker', 'big')])

	def testDeclaration(self):
		round = Round(self.num_players, deck_name='declaration')
		self.assertEqual(round.state.trump_card.suit, None)
		round.deal_card()
		# Have the first player declare the 2 of diamonds.
		round.declare(self.first_player, [Card('d', '2')])
		# Deal out the remaining cards.
		for _ in range(len(round.state.deck)):
			round.deal_card()
		# Verify the bottom hasn't been given yet.
		self.assertEqual(len(round.state.player_hands[self.first_player]), self.full_hand_size)
		round.finalize_declaration()
		# Verify the bottom was given.
		self.assertEqual(len(round.state.player_hands[self.first_player]), self.full_hand_with_bottom_size)
		round.set_bottom(self.first_player, self.declaration_bottom_cards)
		# Verify the round status is now playing and the trump suit is correct.
		self.assertEqual(round.state.status, STATUS_PLAYING)
		self.assertEqual(round.state.trump_card.suit, 'd')

	def testDeclarationOverturning(self):
		round = Round(self.num_players, deck_name='declaration')
		round.deal_card()
		# Have the first player declare the 2 of diamonds.
		round.declare(self.first_player, [Card('d', '2')])
		# Deal enough cards so the other players have trump values in their hands.
		for _ in range(20):
			round.deal_card()
		round.declare(self.third_player, [Card('s', '2'), Card('s', '2')])
		# Deal out the remaining cards.
		for _ in range(len(round.state.deck)):
			round.deal_card()
		self.assertEqual(len(round.state.player_hands[self.third_player]), self.full_hand_size)
		round.finalize_declaration()
		self.assertEqual(len(round.state.player_hands[self.third_player]), self.full_hand_with_bottom_size)
		round.set_bottom(self.third_player, self.declaration_bottom_cards)
		# Verify the round status is now playing and the trump suit is correct.
		self.assertEqual(round.state.status, STATUS_PLAYING)
		self.assertEqual(round.state.trump_card.suit, 's')

	def testDeclarationDefending(self):
		round = Round(self.num_players, deck_name='declaration')
		# Deal enough cards so the third player has one 2 of spades.
		for _ in range(4):
			round.deal_card()
		round.declare(self.third_player, [Card('s', '2')])
		# Deal enough cards so the third player has two 2 of spades.
		for _ in range(20):
			round.deal_card()
		round.declare(self.third_player, [Card('s', '2'), Card('s', '2')])
		# Deal out the remaining cards.
		for _ in range(len(round.state.deck)):
			round.deal_card()
		self.assertEqual(len(round.state.player_hands[self.third_player]), self.full_hand_size)
		round.finalize_declaration()
		self.assertEqual(len(round.state.player_hands[self.third_player]), self.full_hand_with_bottom_size)
		round.set_bottom(self.third_player, self.declaration_bottom_cards)
		# Verify the round status is now playing and the trump suit is correct.
		self.assertEqual(round.state.status, STATUS_PLAYING)
		self.assertEqual(round.state.trump_card.suit, 's')

	def testNoDeclaration(self):
		round = Round(self.num_players, deck_name='declaration')
		self.assertEqual(round.state.trump_card.suit, None)
		# Deal out the remaining cards.
		for _ in range(len(round.state.deck)):
			round.deal_card()
		self.assertEqual(round.state.trump_card.suit, None)
		self.assertEqual(len(round.state.player_hands[self.first_player]), self.full_hand_size)
		round.finalize_declaration()
		self.assertEqual(len(round.state.player_hands[self.first_player]), self.full_hand_with_bottom_size)
		round.set_bottom(self.first_player, self.declaration_bottom_cards)
		# Verify the round status is now playing and the trump suit is correct.
		self.assertEqual(round.state.status, STATUS_PLAYING)
		self.assertEqual(round.state.trump_card.suit, 'joker')

class TestRoundState(unittest.TestCase):
	# TODO(workitem0028): will add flush validation tests once flush capability is integrated
	def setUp(self):
		self.num_players = 6
		self.first_player = 0
		self.second_player = 1
		self.third_player = 2
		self.round_state = RoundState(self.num_players)
		self.round_state.trump_card = Card('c', '3')
		self.round_state.player_hands[self.second_player] = [
			Card('s', '4'), Card('s', '5'), Card('s', '5'), Card('s', '10'), Card('s', 'K'),
			Card('h', '5'),
			Card('c', '8'), Card('c', '8'), Card('c', '8'), Card('h', '3'), Card('s', '3'), Card('s', '3'),
			Card('c', '3'), Card('c', '3'), Card('joker', 'small'), Card('joker', 'small')
		]

	@parameterized.expand([
		[
			'one trick - no points',
			[
				[
					[Card('d', '7'), Card('d', '7')],
					[Card('d', '8'), Card('d', '3')],
					[Card('d', 'A'), Card('d', '3')],
					[Card('d', '9'), Card('d', '9')],
					[Card('d', 'Q'), Card('d', 'Q')],
					[Card('d', '4'), Card('d', 'J')],
				],
			],
			[[0, 0, 0, 0, 0, 0]]
		],
		[
			'one trick - points',
			[
				[
					[Card('d', '7'), Card('d', '7')],
					[Card('d', '10'), Card('d', '2')],
					[Card('d', '5'), Card('d', '2')],
					[Card('d', '9'), Card('d', '9')],
					[Card('d', 'K'), Card('d', 'K')],
					[Card('d', '10'), Card('d', 'J')],
				],
			],
			[[0, 0, 0, 0, 45, 0]]
		],
		[
			'multiple tricks - different player wins points',
			[
				[
					[Card('d', '7'), Card('d', '7')],
					[Card('d', '10'), Card('d', '2')],
					[Card('d', '5'), Card('d', '2')],
					[Card('d', '9'), Card('d', '9')],
					[Card('d', 'K'), Card('d', 'K')],
					[Card('d', '10'), Card('d', 'J')],
				],
				[
					[Card('s', '5')],
					[Card('s', 'A')],
					[Card('s', '10')],
					[Card('s', '2')],
					[Card('s', 'K')],
					[Card('s', '2')],
				],
			],
			[[0, 0, 0, 0, 45, 0], [0, 25, 0, 0, 45, 0]]
		],
		[
			'multiple tricks - same player wins points',
			[
				[
					[Card('d', '7'), Card('d', '7')],
					[Card('d', '10'), Card('s', '2')],
					[Card('d', '5'), Card('d', '2')],
					[Card('d', '9'), Card('d', '9')],
					[Card('d', 'K'), Card('d', 'K')],
					[Card('h', '10'), Card('c', 'J')],
				],
				[
					[Card('s', '5')],
					[Card('s', 'K')],
					[Card('s', '10')],
					[Card('s', '2')],
					[Card('s', 'A')],
					[Card('s', '2')],
				],
			],
			[[0, 0, 0, 0, 45, 0], [0, 0, 0, 0, 70, 0]]
		],
	])

	def testPlayerPoints(self, name, trick_plays, cumulative_player_points):
		for i, trick in enumerate(trick_plays):
			self.round_state.board = trick
			self.round_state.end_trick()
			self.assertEqual(self.round_state.player_points, cumulative_player_points[i])

	@parameterized.expand([
		['even number of players - attacking team given first player bottom', 0, [1, 3, 5]],
		['even number of players - attacking team given second player bottom', 1, [0, 2, 4]],
	])

	def testSetAttackingPlayers(self, name, bottom_player, expected_attacking_team):
		self.round_state.bottom_player = bottom_player
		self.round_state.set_attacking_players()
		self.assertEqual(self.round_state.attacking_players, expected_attacking_team)

	@parameterized.expand([
		['diamonds', Card('d', '2'), []],
		['hearts', Card('h','2'), [
			{'rank': 1, 'length': 1, 'power_card': Card('h', '5'), 'suit_type': SUIT_TRICK}]
		],
		['spades', Card('s', '2'), [
			{'rank': 2, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', 'K'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', '10'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_TRICK}]
		],
		['trump', Card('c', '2'), [
			{'rank': 3, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
			{'rank': 2, 'length': 3, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_TRUMP}]
		],
		['trump', Card('h', '3'), [
			{'rank': 3, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRUMP},
			{'rank': 2, 'length': 3, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_TRUMP}]
		],
	])

	def testSuitTractorsFromHandNonJokerTrump(self, suit_name, trick_card, suit_tractor_data):
		suit_tractors = tractor_generator(suit_tractor_data, self.round_state.trump_card)
		hand = self.round_state.player_hands[self.second_player]
		trick_suit = trick_card.get_normalized_suit(self.round_state.trump_card)
		self.assertEqual(self.round_state.get_suit_tractors_from_cards(hand, trick_suit), suit_tractors)

	@parameterized.expand([
		['diamonds', Card('d', '2'), []],
		['hearts', Card('h','2'), [
			{'rank': 1, 'length': 1, 'power_card': Card('h', '5'), 'suit_type': SUIT_TRICK}]
		],
		['spades', Card('s', '2'), [
			{'rank': 2, 'length': 1, 'power_card': Card('s', '5'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', 'K'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', '10'), 'suit_type': SUIT_TRICK},
			{'rank': 1, 'length': 1, 'power_card': Card('s', '4'), 'suit_type': SUIT_TRICK}]
		],
		['clubs', Card('c', '2'), [
			{'rank': 3, 'length': 1, 'power_card': Card('c', '8'), 'suit_type': SUIT_TRICK}],
		],
		['trump', Card('joker', 'small'), [
			{'rank': 2, 'length': 2, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 2, 'length': 1, 'power_card': Card('c', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_TRUMP}]
		],
		['trump', Card('c', '3'), [
			{'rank': 2, 'length': 2, 'power_card': Card('s', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 2, 'length': 1, 'power_card': Card('c', '3'), 'suit_type': SUIT_TRUMP},
			{'rank': 1, 'length': 1, 'power_card': Card('h', '3'), 'suit_type': SUIT_TRUMP}]
		],
	])

	def testSuitTractorsFromHandJokerTrump(self, suit_name, trick_card, suit_tractor_data):
		self.round_state.trump_card = Card('joker', '3')
		suit_tractors = tractor_generator(suit_tractor_data, self.round_state.trump_card)
		hand = self.round_state.player_hands[self.second_player]
		trick_suit = trick_card.get_normalized_suit(self.round_state.trump_card)
		self.assertEqual(self.round_state.get_suit_tractors_from_cards(hand, trick_suit), suit_tractors)

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
		self.assertFalse(self.round_state.is_play_valid(self.first_player, play))

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
		self.assertTrue(self.round_state.is_play_valid(self.first_player, play))

	@parameterized.expand(model_test_data.follow_suit_validity_test_data)

	def testFollowSuitValidity(self, name, first_play, invalid_play, valid_play):
		self.round_state.board[0] = first_play
		self.assertFalse(self.round_state.is_play_valid(self.second_player, invalid_play))
		self.assertTrue(self.round_state.is_play_valid(self.second_player, valid_play))

	@parameterized.expand(model_test_data.follow_suit_validity_custom_hand_test_data)

	def testFollowSuitValidityWithCustomHand(self, name, first_play, hand, invalid_play, valid_play):
		first_play, hand, invalid_play, valid_play = test_utils.apply_cards_from_str(first_play, hand, invalid_play, valid_play)
		self.round_state.board[0] = first_play
		self.round_state.player_hands[self.third_player] = hand
		if invalid_play is not None:
			self.assertFalse(self.round_state.is_play_valid(self.third_player, invalid_play))
		if valid_play is not None:
			self.assertTrue(self.round_state.is_play_valid(self.third_player, valid_play))

	@parameterized.expand([
		['no play', [], []],

		['too many cards', [Card('s', '3'), Card('s', '3'), Card('s', '4')], []],

		['cards not in player hand', [Card('h', '3')], []],

		['card value does not match trump value', [Card('s', '4')], []],

		['cards do not have the same suit', [Card('s', '3'), Card('d', '3')], []],

		['equal length to most recent declaration', [Card('s', '3')],
			[Declaration(1, [Card('d', '3')])]],

		['smaller length than most recent declaration', [Card('s', '3')],
			[Declaration(1, [Card('d', '3')]), Declaration(1, [Card('d', '3'), Card('d', '3')])]],

		['suit does not match previous declaration', [Card('s', '3'), Card('s', '3')],
			[Declaration(0, [Card('d', '3')])]],

		['one joker', [Card('joker', 'big')], []],

		['overturning themselves with jokers', [Card('joker', 'big'), Card('joker', 'big')],
		  [Declaration(0, [Card('d', '3')])]],

		['overturning two small cards with big / small joker combo', [Card('joker', 'small'), Card('joker', 'big')],
		  [Declaration(1, [Card('d', '3'), Card('d', '3')])]],

		['two small jokers overturning two big jokers', [Card('joker', 'small'), Card('joker', 'small')],
		  [Declaration(1, [Card('joker', 'big'), Card('joker', 'big')])]],

		['two big jokers overturning two big jokers', [Card('joker', 'big'), Card('joker', 'big')],
		  [Declaration(1, [Card('joker', 'big'), Card('joker', 'big')])]],
	])

	def testInvalidDeclarations(self, name, cards, declarations):
		player = 0
		self.round_state.declarations = declarations
		self.round_state.player_hands[player] = [
			Card('s', '4'), Card('s', '3'), Card('s', '3'),
			Card('d', '3'), Card('joker', 'small'), Card('joker', 'small'),
			Card('joker', 'big'), Card('joker', 'big'),
		]
		self.assertFalse(self.round_state.is_declaration_valid(player, cards))

	@parameterized.expand([
		['initial play with a single', [Card('s', '3')], []],

		['initial play with a pair', [Card('s', '3'), Card('s', '3')], []],

		['overturn another declaration', [Card('s', '3'), Card('s', '3')],
			[Declaration(1, [Card('d', '3')])]],

		['overturn another declaration with rank 3', [Card('s', '3'), Card('s', '3'), Card('s', '3')],
			[Declaration(1, [Card('d', '3')])]],

		['defend previous declaration', [Card('s', '3'), Card('s', '3')],
			[Declaration(0, [Card('s', '3')])]],

		['defend previous declaration with rank 3', [Card('s', '3'), Card('s', '3'), Card('s', '3')],
			[Declaration(0, [Card('s', '3')])]],

		['start with two jokers', [Card('joker', 'big'), Card('joker', 'big')], []],

		['overturning someone else with jokers', [Card('joker', 'big'), Card('joker', 'big')],
		  [Declaration(1, [Card('d', '3')])]],

		['overturning pair with jokers', [Card('joker', 'big'), Card('joker', 'big')],
		  [Declaration(1, [Card('d', '3'), Card('d', '3')])]],

		['overturning small jokers with big jokers', [Card('joker', 'big'), Card('joker', 'big')],
		  [Declaration(1, [Card('joker', 'small'), Card('joker', 'small')])]],

		['overturning with jokers after declaring once already', [Card('joker', 'big'), Card('joker', 'big')],
		  [Declaration(0, [Card('s', '3')]), Declaration(1, [Card('h', '3'), Card('h', '3')])]],

		['overturn two big jokers with rank 3', [Card('s', '3'), Card('s', '3'), Card('s', '3')],
			[Declaration(1, [Card('joker', 'big'), Card('joker', 'big')])]],
	])

	def testValidDeclarations(self, name, cards, declarations):
		player = 0
		self.round_state.declarations = declarations
		self.round_state.player_hands[player] = [
			Card('s', '4'), Card('s', '3'), Card('s', '3'), Card('s', '3'),
			Card('d', '3'), Card('joker', 'big'), Card('joker', 'big'),
		]
		self.assertTrue(self.round_state.is_declaration_valid(player, cards))

if __name__ == '__main__':
	unittest.main()
