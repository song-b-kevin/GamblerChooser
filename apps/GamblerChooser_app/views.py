from django.shortcuts import render, redirect
from django.contrib import messages
from random import *

# Card deck creation


class Card():
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        names = {
            1: "Ace",
            11: "Jack",
            12: "Queen",
            13: "King"
        }
        self.name = names.get(value) or str(value)

    def show_value(self):
        return (f"{self.name} of {self.suit}")


class Deck():
    def __init__(self):
        self.cards = []

        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            for value in range(1, 14):
                self.cards.append(Card(value, suit))

    def shuffle_single(self):
        shuffled_deck = []
        cut_index = randint(20, int(len(self.cards)/2))
        for index in range(cut_index):
            shuffled_deck.append(self.cards[cut_index+index])
            shuffled_deck.append(self.cards[index])
        for index in range(cut_index*2, len(self.cards)):
            shuffled_deck.append(self.cards[index])
        self.cards = shuffled_deck

    def shuffle(self, times=50):
        for time in range(times):
            self.shuffle_single()
        return self

    def sort(self):
        sorted_deck = {
            "Hearts": [],
            "Diamonds": [],
            "Clubs": [],
            "Spades": []
        }
        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            for card in self.cards:
                if card.suit == suit:
                    sorted_deck[suit].append(card)
            for deck_suit in sorted_deck[suit]:
                for i in range(len(sorted_deck[suit])-1):
                    for j in range(len(sorted_deck[suit])-1-i):
                        if sorted_deck[suit][j].value > sorted_deck[suit][j+1].value:
                            sorted_deck[suit][j], sorted_deck[suit][j+1] = sorted_deck[suit][j+1], sorted_deck[suit][j]
        final_deck = []
        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            for card in sorted_deck[suit]:
                final_deck.append(card)
        self.cards = final_deck

    def draw_card(self):
        return self.cards.pop()

    def game(self, number_of_players, player_names):
        # players[i] = {
        #   name
        #   hand - two cards
        #   final_hand - hand + community cards
        #   best_hand{display, rank, high_card, suit}
        # }
        players = []
        # Deal to players
        for i in range(number_of_players):
            players.append({"name": player_names[i]})
            players[i]["hand"] = [self.draw_card()]
        for i in range(number_of_players):
            players[i]["hand"].append(self.draw_card())
        # Deal flop
        dealer = {
            "burn_pile": [self.draw_card()],
            "community": []
        }
        for i in range(3):
            dealer["community"].append(self.draw_card())
        # Deal turn
        dealer["burn_pile"].append(self.draw_card())
        dealer["community"].append(self.draw_card())
        # Deal river
        dealer["burn_pile"].append(self.draw_card())
        dealer["community"].append(self.draw_card())
        # Check players hands
        for i in range(number_of_players):
            players[i]["final_hand"] = []
            for card in dealer["community"]:
                players[i]["final_hand"].append(card)
            for j in range(2):
                players[i]["final_hand"].append(players[i]["hand"][j])
            ## rank:
            # 0 | high card
            # 1 | pair
            # 2 | two pair
            # 3 | three of a kind
            # 4 | straight
            # 5 | flush
            # 6 | full house
            # 7 | four of a kind
            # 8 | straight flush
            # 9 | royal flush
            players[i]["best_hand"] = {
                "display": "None",
                "rank": 0,
                "high_card": [0],
                "suit": 0
            }
            ## Check duplicates
            dup_counter = {}
            for card in players[i]["final_hand"]:
                if card.value not in dup_counter:
                    dup_counter[card.value] = 1
                else:
                    dup_counter[card.value] += 1
            for card_value in dup_counter:
                # Four of a kind
                if dup_counter[card_value] == 4 and players[i]["best_hand"]["rank"] < 2:
                    # Change high card value = quad
                    players[i]["best_hand"]["high_card"] = [card_value]
                    # Change rank = 7
                    players[i]["best_hand"]["rank"] = 7
                # Three of a kind
                elif dup_counter[card_value] == 3 and players[i]["best_hand"]["rank"] <= 3:
                    # Existing three of a kind
                    if players[i]["best_hand"]["rank"] == 3:
                        # Change high card values [pair, triple]
                        if players[i]["best_hand"]["high_card"][0] > card_value:
                            players[i]["best_hand"]["high_card"] = [
                                card_value, players[i]["best_hand"]["high_card"][0]]
                        else:
                            players[i]["best_hand"]["high_card"] = [
                                players[i]["best_hand"]["high_card"][0], card_value]
                        # Change rank = 6
                        players[i]["best_hand"]["rank"] = 6
                    # Existing two pairs
                    elif players[i]["best_hand"]["rank"] == 2:
                        # Change high card values [pair, triple]
                        if players[i]["best_hand"]["high_card"][0] > players[i]["best_hand"]["high_card"][1]:
                            players[i]["best_hand"]["high_card"] = [
                                players[i]["best_hand"]["high_card"][0], card_value]
                        else:
                            players[i]["best_hand"]["high_card"] = [
                                players[i]["best_hand"]["high_card"][1], card_value]
                        # Change rank = 6
                        players[i]["best_hand"]["rank"] = 6
                    # Existing pair
                    elif players[i]["best_hand"]["rank"] == 1:
                        # Change high card value [pair, triple]
                        players[i]["best_hand"]["high_card"] = [
                            players[i]["best_hand"]["high_card"][0], card_value]
                        # Change rank = 6
                        players[i]["best_hand"]["rank"] = 6
                    # Initiate three of a kind
                    else:
                        # Change high card value = triple
                        players[i]["best_hand"]["high_card"] = [card_value]
                        # Change rank = 3
                        players[i]["best_hand"]["rank"] = 3
                # Pair
                elif dup_counter[card_value] == 2:
                    # Existing full house
                    if players[i]["best_hand"]["rank"] == 6:
                        # Check if higher pair
                        if card_value > players[i]["best_hand"]["high_card"][0]:
                            # Change high card value = [pair, triple]
                            players[i]["best_hand"]["high_card"][0] = card_value
                    # Existing three of a kind
                    elif players[i]["best_hand"]["rank"] == 3:
                        # Change high card value = [pair, triple]
                        players[i]["best_hand"]["high_card"] = [
                            card_value, players[i]["best_hand"]["high_card"][0]]
                        # Change rank = 6
                        players[i]["best_hand"]["rank"] = 6
                    # Existing two pairs
                    elif players[i]["best_hand"]["rank"] == 2:
                        # Check if ace
                        if card_value == 1:
                            if players[i]["best_hand"]["high_card"][0] > players[i]["best_hand"]["high_card"][1]:
                                # Change high card value = [low, high]
                                players[i]["best_hand"]["high_card"][1] = card_value
                            else:
                                # Change high card value = [low, high]
                                players[i]["best_hand"]["high_card"] = [
                                    players[i]["best_hand"]["high_card"][1], card_value]
                        # Check if higher pair
                        elif card_value > players[i]["best_hand"]["high_card"][1] and players[i]["best_hand"]["high_card"][1] != 1:
                            # Change high card value = [low, high]
                            players[i]["best_hand"]["high_card"] = [
                                players[i]["best_hand"]["high_card"][1], card_value]
                        elif card_value > players[i]["best_hand"]["high_card"][0] and players[i]["best_hand"]["high_card"][0] != 1:
                            # Change high card value = [low, high]
                            players[i]["best_hand"]["high_card"][0] = card_value
                    # Initiate two pairs
                    elif players[i]["best_hand"]["rank"] == 1:
                        # Change high card = [low, high]
                        if players[i]["best_hand"]["high_card"][0] == 1:
                            players[i]["best_hand"]["high_card"] = [
                                card_value, players[i]["best_hand"]["high_card"][0]]
                        elif card_value > players[i]["best_hand"]["high_card"][0] or card_value == 1:
                            players[i]["best_hand"]["high_card"] = [
                                players[i]["best_hand"]["high_card"][0], card_value]
                        else:
                            players[i]["best_hand"]["high_card"] = [
                                card_value, players[i]["best_hand"]["high_card"][0]]
                        # Change rank = 2
                        players[i]["best_hand"]["rank"] = 2
                    # Initiate first pair
                    elif players[i]["best_hand"]["rank"] == 0:
                        # Change high card = pair
                        players[i]["best_hand"]["high_card"] = [card_value]
                        # Change rank = 1
                        players[i]["best_hand"]["rank"] = 1
                # High Card
                elif dup_counter[card_value] == 1 and players[i]["best_hand"]["rank"] == 0:
                    # Check if higher card value
                    if card_value == 1:
                        # Change high card value = High card
                        players[i]["best_hand"]["high_card"] = [card_value]
                    elif card_value > players[i]["best_hand"]["high_card"][0] and players[i]["best_hand"]["high_card"][0] != 1:
                        # Change high card value = High card
                        players[i]["best_hand"]["high_card"] = [card_value]
            ## Check straight
            # Sort hand by value
            players[i]["final_hand"] = sorted(players[i]["final_hand"], key=lambda x: x.value)
            # sorted_hand = {card_values: [card_suits]}
            sorted_hand = {}
            for card in players[i]["final_hand"]:
                if card.value not in sorted_hand:
                    sorted_hand[card.value] = [card.suit]
                else:
                    sorted_hand[card.value].append(card.suit)
            # Check if ace and king in hand
            if 1 in sorted_hand and 13 in sorted_hand:
                for suit in sorted_hand[1]:
                    if 14 not in sorted_hand:
                        sorted_hand[14] = [suit]
                    else:
                        sorted_hand[14].append(suit)
            # Counter for straights and flush
            straight_counter = 1
            suit_counter = ["", 1]
            for card_value in sorted_hand:
                if (card_value+1) in sorted_hand:
                    straight_counter += 1
                    suit_checked = False
                    for suit in sorted_hand[card_value]:
                        if not suit_checked:
                            if suit in sorted_hand[card_value+1]:
                                suit_counter[0] = suit
                                suit_counter[1] += 1
                                suit_checked = True
                    if not suit_checked:
                        suit_counter[0] = ""
                        suit_counter[1] = 1
                else:
                    straight_counter = 1
                if straight_counter >= 5:
                    # Initiate royal flush
                    if suit_counter[1] >= 5 and (card_value+1) == 14:
                        # Change high card value = royal flush
                        players[i]["best_hand"]["high_card"][0] = card_value+1
                        # Change rank = 9
                        players[i]["best_hand"]["rank"] = 9
                    # Initiate straight flush
                    elif suit_counter[1] >= 5:
                        # Change high card value = straight flush
                        players[i]["best_hand"]["high_card"][0] = card_value+1
                        # Change rank = 8
                        players[i]["best_hand"]["rank"] = 8
                    # Initiate straight
                    elif players[i]["best_hand"]["rank"] <= 4:
                        # Change high card value = straight
                        players[i]["best_hand"]["high_card"][0] = card_value+1
                        # Change rank = 4
                        players[i]["best_hand"]["rank"] = 4
            ## Check flush
            suit_counter = {
                "Hearts": [0,[]],
                "Diamonds": [0,[]],
                "Clubs": [0,[]],
                "Spades": [0,[]]
            }
            for card in players[i]["final_hand"]:
                suit_counter[card.suit][0] += 1
                suit_counter[card.suit][1].append(card.value)
            for key in suit_counter:
                if suit_counter[key][0] > 4:
                    # Initiate flush
                    if players[i]["best_hand"]["rank"] < 5:
                        # Change high card value = flush
                        if suit_counter[key][1][0] == 1:
                            players[i]["best_hand"]["high_card"] = [suit_counter[key][1][0]]
                        else:
                            players[i]["best_hand"]["high_card"] = [suit_counter[key][1][len(suit_counter[key][1])-1]]
                        # Change rank = 5
                        players[i]["best_hand"]["rank"] = 5
                        # Change suit
                        players[i]["best_hand"]["suit"] = key
        # Check winner
        winner = None
        for i in range(number_of_players):
            # Convert suit to value
            if players[i]["best_hand"]["suit"] == "Spades":
                players[i]["best_hand"]["suit"] = 4
            elif players[i]["best_hand"]["suit"] == "Hearts":
                players[i]["best_hand"]["suit"] = 3
            elif players[i]["best_hand"]["suit"] == "Clubs":
                players[i]["best_hand"]["suit"] = 2
            elif players[i]["best_hand"]["suit"] == "Diamonds":
                players[i]["best_hand"]["suit"] = 1
            # Convert high card value of ace = 14
            for j in range(len(players[i]["best_hand"]["high_card"])):
                if players[i]["best_hand"]["high_card"][j] == 1:
                    players[i]["best_hand"]["high_card"][j] = 14
            # Check higher rank
            if winner == None or winner["best_hand"]["rank"] < players[i]["best_hand"]["rank"]:
                winner = players[i]
            # Check equal rank and higher card value
            elif winner["best_hand"]["rank"] == players[i]["best_hand"]["rank"] and winner["best_hand"]["high_card"] < players[i]["best_hand"]["high_card"]:
                winner = players[i]
            # Check equal rank and equal card value
            elif winner["best_hand"]["rank"] == players[i]["best_hand"]["rank"] and winner["best_hand"]["high_card"] == players[i]["best_hand"]["high_card"] and winner["best_hand"]["suit"] > players[i]["best_hand"]["suit"]:
                winner = players[i]
        # Change display
        for i in range(number_of_players):
            for j in range(len(players[i]["best_hand"]["high_card"])):
                ## Change aces and face cards
                # Ace
                if players[i]["best_hand"]["high_card"][j] == 14:
                    players[i]["best_hand"]["high_card"][j] = "Ace"
                # Jack
                elif players[i]["best_hand"]["high_card"][j] == 11:
                    players[i]["best_hand"]["high_card"][j] = "Jack"
                # Queen
                elif players[i]["best_hand"]["high_card"][j] == 12:
                    players[i]["best_hand"]["high_card"][j] = "Queen"
                # King
                elif players[i]["best_hand"]["high_card"][j] == 13:
                    players[i]["best_hand"]["high_card"][j] = "King"
                ## Change displays
                # High card
                if players[i]["best_hand"]["rank"] == 0:
                    players[i]["best_hand"]["display"] = f"High Card - {players[i]['best_hand']['high_card'][0]}"
                # Pair
                elif players[i]["best_hand"]["rank"] == 1:
                    players[i]["best_hand"]["display"] = f"Pair of {players[i]['best_hand']['high_card'][0]}s"
                # Two pair
                elif players[i]["best_hand"]["rank"] == 2:
                    players[i]["best_hand"]["display"] = f"Two pair - {players[i]['best_hand']['high_card'][0]}s & {players[i]['best_hand']['high_card'][1]}s"
                # Three of a kind
                elif players[i]["best_hand"]["rank"] == 3:
                    players[i]["best_hand"]["display"] = f"Three of a kind - {players[i]['best_hand']['high_card'][0]}s"
                # Straight
                elif players[i]["best_hand"]["rank"] == 4:
                    players[i]["best_hand"]["display"] = f"Straight - {players[i]['best_hand']['high_card'][0]} high"
                # Flush
                elif players[i]["best_hand"]["rank"] == 5:
                    players[i]["best_hand"]["display"] = f"Flush - {players[i]['best_hand']['high_card'][0]} high"
                # Full house
                elif players[i]["best_hand"]["rank"] == 6:
                    players[i]["best_hand"]["display"] = f"Full house - {players[i]['best_hand']['high_card'][1]}s over {players[i]['best_hand']['high_card'][0]}s"
                # Four of a kind
                elif players[i]["best_hand"]["rank"] == 7:
                    players[i]["best_hand"]["display"] = f"Four of a kind - {card_value}s"
                # Straight flush
                elif players[i]["best_hand"]["rank"] == 8:
                    players[i]["best_hand"]["display"] = f"Straight flush - {players[i]['best_hand']['high_card'][0]} high"
                # Royal flush
                elif players[i]["best_hand"]["rank"] == 9:
                    players[i]["best_hand"]["display"] = "Royal flush!!!"
        return {
            "players": players,
            "dealer": dealer,
            "winner": winner
        }

# Create your views here.


def index(request):
    if "players" not in request.session:
        request.session["players"] = []
    context = {
        "all_players": request.session["players"],
        "player_number": len(request.session["players"])
    }
    return render(request, "GamberChooser_app/index.html", context)


def add_players(request):
    if request.POST["player"] != "":
        if len(request.session["players"]) < 5:
            request.session["players"].append(request.POST["player"])
            request.session.modified = True
        else:
            messages.error(request, "Maximum 5 players.")
    else:
        messages.error(request, "Must enter a player name.")
    return redirect("/")

def remove_player(request, player_id):
    print(int(player_id))
    request.session["players"].pop(int(player_id))
    request.session.modified = True
    return redirect("/")


def play_game(request):
    if len(request.session["players"]) < 2:
        messages.error(request, "Must have at least 2 players.")
        return redirect("/")
    game = Deck().shuffle().game(
        len(request.session["players"]), request.session["players"])
    context = {
        "players": game["players"],
        "burn_pile": game["dealer"]["burn_pile"],
        "community": game["dealer"]["community"],
        "winner": game["winner"]
    }
    return render(request, "GamberChooser_app/play_game.html", context)


def new_game(request):
    request.session.clear()
    return redirect("/")