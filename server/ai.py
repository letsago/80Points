import model
from tractor import Tractor, TractorMetadata, Flush, card_to_suit_type, cards_to_tractors, SUIT_TRUMP
from tractor import find_matching_data_index, update_data_array, get_min_data
import eventlet, random

DEBUG = False

def get_ai_move(state, player_idx):
	'''
	Get an automatic move.
	The AI player only considers the current board state.
	It has no memory of previous tricks.
	Arguments:
	- state: RoundState
	- player_idx: int AI player index
	Returns Card [].
	This code is only intended for 4-player games and may not work with flushes.
	'''

	n = state.num_players
	if n != 4:
		raise Exception("get_ai_move only supports num_players=4")

	# use separate logic if we're starting a new trick
	if state.is_board_full() or state.is_board_empty():
		return get_ai_first_move(state, player_idx)

	board, first_player = state.board, state.trick_first_player

	# did all of our allies play earlier in the trick?
	allies = [(player_idx+2)%n]
	all_allies_played = True
	for ally_idx in allies:
		if (ally_idx - first_player) % n >= (player_idx - first_player) % n:
			continue
		all_allies_played = False

	# is an ally currently winning the trick?
	winning_player, winning_flush = state.determine_winner()
	ally_winning = winning_player in allies

	# get our hand and tractors in the first play
	first_play = state.board[first_player]
	trick_card = first_play[0]
	trick_suit = trick_card.get_normalized_suit(state.trump_card)
	first_tractors = cards_to_tractors(first_play, trick_card.suit, state.trump_card)
	hand = state.player_hands[player_idx]

	# pickers are functions that select cards with some policy (e.g., most points)
	# we apply the policy by repeatedly using it to select some cards to play
	# picker is a function(data, exact_tractors, larger_tractors) -> Card []
	# exact_tractors have same length and rank as priority_data, while larger_tractors
	# have higher length and/or rank
	def apply_picker(picker):
		# create copy of hand that we'll remove cards from as cards are selected for playing
		pick_hand = list(hand)
		picked_cards = []
		first_data = [TractorMetadata(tractor.rank, tractor.length) for tractor in first_tractors]
		while first_data:
			# compute the minimum rank/length tractor we must play
			suit_tractors = state.get_suit_tractors_from_cards(pick_hand, trick_suit)
			hand_data = [TractorMetadata(tractor.rank, tractor.length) for tractor in suit_tractors]
			if len(hand_data) == 0:
				break
			hand_idx = find_matching_data_index(hand_data, first_data[0])
			min_data = get_min_data(first_data[0], hand_data[hand_idx])

			# get tractors that exactly match the minimum, and tractors that are larger in rank/length
			exact = []
			larger = []
			for tractor in suit_tractors:
				if tractor.rank == min_data.rank and tractor.length == min_data.length:
					exact.append(tractor)
				elif tractor.rank >= min_data.rank and tractor.length >= min_data.length:
					larger.append(tractor)

			# run the picker
			cur_picked = picker(min_data, exact, larger)
			for card in cur_picked:
				picked_cards.append(card)
				pick_hand.remove(card)

			first_data = update_data_array(first_data, min_data)

		# at this point there should be no cards in suit matching first_play
		# so we provide single cards to the picker
		while len(picked_cards) < len(first_play):
			exact = []
			for card in pick_hand:
				suit_type = card_to_suit_type(card, trick_card.suit, state.trump_card)
				tractor = Tractor(1, 1, card.suit_power(state.trump_card), suit_type)
				tractor.orig_cards = [[card]]
				exact.append(tractor)
			cur_picked = picker(TractorMetadata(1, 1), exact, [])
			for card in cur_picked:
				picked_cards.append(card)
				pick_hand.remove(card)

		return picked_cards

	# for each priority data, pick a tractor from the hand tractors to add
	# if ally_winning, then try to play points
	# otherwise, try to win the trick (play highest cards)
	# if we can't win, then play low cards
	if ally_winning:
		cards = apply_picker(points_picker)
		if DEBUG: print('ally is winning, points picker yields {}'.format(cards))
		return cards

	high_cards = apply_picker(high_picker)
	my_tractors = cards_to_tractors(high_cards, trick_card.suit, state.trump_card, target_form=winning_flush.tractors)
	if DEBUG: print('no ally winning, high picker yields {} versus {}'.format(high_cards, winning_flush.tractors))
	if my_tractors is not None and Flush(my_tractors) > winning_flush:
		return high_cards

	low_cards = apply_picker(low_picker)
	if DEBUG: print('high cards lost, low picker yields {}'.format(low_cards))
	return low_cards

# get splits of a large tractor that matches form with a smaller tractor
# this function retains the orig_cards set in cards_from_tractors
def get_splits(large, small):
	# first split the length, then for each split, cut the rank
	splits = []
	for i in range(large.length - small.length + 1):
		tractor = Tractor(large.rank, small.length, large.power + i, large.suit_type)
		tractor.orig_cards = large.orig_cards[i:i+small.length]
		splits.append(tractor)
	for split in splits:
		split.rank = small.rank
		split.orig_cards = [t[:small.rank] for t in split.orig_cards]
	return splits

# flattens list of list of cards
def flatten(x):
	cards = []
	for l in x:
		for card in l:
			cards.append(card)
	return cards

# picker that plays as low or high as possible
def cmp_picker(data, exact, larger, cmp_func):
	best_tractor = None
	best_cards = None
	for tractor in exact:
		if best_tractor is None or cmp_func(tractor, best_tractor):
			best_tractor = tractor
			best_cards = flatten(tractor.orig_cards)

	if best_cards is not None:
		return best_cards

	for tractor in larger:
		for split in get_splits(tractor, data):
			if best_tractor is None or cmp_func(split, best_tractor):
				best_tractor = split
				best_cards = flatten(split.orig_cards)

	return best_cards

def low_picker(data, exact, larger):
	def f(t1, t2):
		points1 = model.get_points(flatten(t1.orig_cards))
		points2 = model.get_points(flatten(t2.orig_cards))
		if points1 != points2:
			return points1 < points2
		return t1 < t2
	return cmp_picker(data, exact, larger, f)
def high_picker(data, exact, larger):
	return cmp_picker(data, exact, larger, lambda t1, t2: t1 > t2)

# picker that maximizes for points
def points_picker(data, exact, larger):
	# if any in exact have positive points, pick the most points in exact
	# otherwise try to provide positive points from larger
	# if none in larger have positive points then return lowest in exact

	best_points = None
	best_cards = None
	for tractor in exact:
		cards = flatten(tractor.orig_cards)
		points = model.get_points(cards)
		if points > 0 and (best_points is None or points > best_points):
			best_points = points
			best_cards = cards

	if best_cards is not None:
		return best_cards

	for tractor in larger:
		for split in get_splits(tractor, data):
			cards = flatten(split.orig_cards)
			points = model.get_points(cards)
			if points > 0 and (best_points is None or points > best_points):
				best_points = points
				best_cards = cards

	if best_cards is not None:
		return best_cards

	return low_picker(data, exact, larger)

def get_ai_first_move(state, player_idx):
	hand = state.player_hands[player_idx]
	tractors = cards_to_tractors(hand, None, state.trump_card)

	# play non-trump highest cards first (possibly as a double)
	# highest card is usually ace unless ace is trump number
	# regardless, the suit power corresponding to this card is always len(CARD_VALUES)-2
	for tractor in tractors:
		if tractor.suit_type != SUIT_TRUMP and tractor.power == len(model.CARD_VALUES)-2:
			return flatten(tractor.orig_cards)

	# next play the highest-rank/longest tractor
	# but exclude 1-rank/1-length tractors
	best_tractor = None
	for tractor in tractors:
		if tractor.rank == 1 and tractor.length == 1:
			continue
		if best_tractor is None or tractor.rank > best_tractor.rank or (tractor.rank == best_tractor.rank and tractor.length > best_tractor.length):
			best_tractor = tractor
	if best_tractor is not None:
		return flatten(best_tractor.orig_cards)

	# play low trump if any
	for tractor in tractors:
		if tractor.suit_type != SUIT_TRUMP:
			continue
		if best_tractor is None or tractor.power < best_tractor.power:
			best_tractor = tractor
	if best_tractor is not None:
		return flatten(best_tractor.orig_cards)

	# play highest card
	for tractor in tractors:
		if best_tractor is None or tractor.power > best_tractor.power:
			best_tractor = tractor
	return flatten(best_tractor.orig_cards)

def get_ai_bottom(state, player_idx):
	'''
	Automatically set a bottom.
	'''
	# select lowest non-trump, non-point single cards
	# if we don't get enough cards from that, select randomly
	hand_copy = list(state.player_hands[player_idx])
	n = len(state.player_hands)
	num_bottom = len(hand_copy) - len(state.player_hands[(player_idx+1)%n])
	tractors = cards_to_tractors(hand_copy, None, state.trump_card)
	selected_cards = []
	for tractor in tractors:
		if tractor.rank > 1 or tractor.length > 1 or tractor.suit_type == SUIT_TRUMP:
			continue
		card = tractor.orig_cards[0][0]
		selected_cards.append(card)
		hand_copy.remove(card)
	selected_cards.sort(key=lambda card: card.suit_power(state.trump_card))
	while len(selected_cards) < num_bottom:
		card = random.choice(hand_copy)
		selected_cards.append(card)
		hand_copy.remove(card)
	return selected_cards[0:num_bottom]

class AIListener(model.RoundListener):
	def __init__(self, player_idx):
		self.player_idx = player_idx

	def card_dealt(self, r, player, card):
		# TODO: automatically declare if it is trump card
		pass

	def _play_on_turn(self, r):
		if r.state.status != model.STATUS_PLAYING:
			return
		if r.state.turn != self.player_idx:
			return
		def play():
			cards = get_ai_move(r.state, self.player_idx)
			r.play(self.player_idx, cards)
		eventlet.spawn_after(0.1, play)

	def player_given_bottom(self, r, player, cards):
		if player != self.player_idx:
			return
		def set_bottom():
			cards = get_ai_bottom(r.state, self.player_idx)
			r.set_bottom(self.player_idx, cards)
		eventlet.spawn_after(1, set_bottom)

	def send_state(self, r):
		# TODO: also try to set bottom if we currently have bottom
		self._play_on_turn(r)

	def player_set_bottom(self, r, player, cards):
		self._play_on_turn(r)

	def player_played(self, r, player, cards):
		self._play_on_turn(r)
