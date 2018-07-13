import random
import math
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

class Player:
    def __init__(self, pos):
        self.pos = pos
        self.in_jail = False
        self.jail_rolls = 0
        self.just_set_free = False
        self.times_landed_on = [0] * 40

    def increment(self, pos):
        self.times_landed_on[pos] += 1

class Board:
    def __init__(self, chance_tiles, community_tiles, chance_deck, community_deck):
        self.chance = chance_tiles
        self.community = community_tiles
        self.chance_deck = chance_deck
        self.community_deck = community_deck

class Game:
    def __init__(self, chance_instance, community_instance):
        self.chance = chance_instance
        self.community = community_instance

def shuffle_deck(master_deck):
    deck_instance = [i for i in master_deck]
    random.shuffle(deck_instance)
    return deck_instance

def dice_sample():
    x = random.uniform(0,1)
    if (x <= 1/6):
        return 1
    elif (x <= 2/6):
        return 2
    elif (x <= 3/6):
        return 3
    elif (x <= 4/6):
        return 4
    elif (x <= 5/6):
        return 5
    else:
        return 6

def roll(player):
    roll_1 = dice_sample()
    roll_2 = dice_sample()
    if player.in_jail:
        if roll_1 != roll_2:
            player.jail_rolls += 1
            if player.jail_rolls != 3:
                player.increment(10)
                return
        if roll_1 == roll_2 or player.jail_rolls == 3:
            player.in_jail = False
            player.just_set_free = True
            player.jail_rolls = 0
    player.pos = (player.pos + (roll_1 + roll_2)) % 40
    player.increment(player.pos)
    # if on special tile draw card
    if player.pos in board.chance:
        draw_card(game.chance, player)
        if len(game.chance) == 0:
            game.chance = shuffle_deck(board.chance_deck)
    elif player.pos in board.community:
        draw_card(game.community, player)
        if len(game.community) == 0:
            game.community = shuffle_deck(board.community_deck)
    # print(game.chance)
    # print(game.community)

    # only roll again if player rolls doubles, and they didn't roll doubles out of jail
    return (roll_1 == roll_2 and not player.just_set_free)

def draw_card(deck, player):
    card_action(deck.pop(0), player)

# according to the card, player moves.
def card_action(card, player):
    if card == 'pass':
        return
    elif isinstance(card, int):
        player.pos = card
        if card == 10:
            player.in_jail = True
    # advance to nearest railroad
    elif card == 'R':
        if player.pos == 7:
            player.pos = 15
        elif player.pos == 22:
            player.pos = 25
        elif player.pos == 36:
            player.pos = 5
    # advance to nearest utility
    elif card == 'U':
        if player.pos == 7 or player.pos == 36:
            player.pos = 12
        elif player.pos == 22:
            player.pos = 28
    # go back 3 spaces
    elif card == 'B':
        player.pos -= 3
    player.increment(player.pos)

def draw(intensities):
    g = nx.Graph()

    # read in the tiles data
    with open('tiles.txt', mode='r') as my_file:
        lines = my_file.readlines()
        tiles = [tile_name.rstrip() for tile_name in lines]

    # add nodes
    for i, tile in enumerate(tiles[:10]):
        x = 100 - 10 * i
        y = 0
        g.add_node(tile, pos=(x, y), label=tile)
    for i, tile in enumerate(tiles[10:20]):
        x = 0
        y = 10 * i
        g.add_node(tile, pos=(x, y), label=tile)
    for i, tile in enumerate(tiles[20:30]):
        x = 10 * i
        y = 100
        g.add_node(tile, pos=(x, y), label=tile)
    for i, tile in enumerate(tiles[30:]):
        x = 100
        y = 100 - 10 * i
        g.add_node(tile, pos=(x, y), label=tile)

    print(tiles)
    print(len(tiles))

    pos = nx.get_node_attributes(g, 'pos')
    labels = nx.get_node_attributes(g, 'label')
    nx.draw_networkx_nodes(g, pos, node_color=intensities, node_size=800, node_shape='s', cmap=plt.cm.Blues)
    nx.draw_networkx_labels(g, pos, labels, font_size=5)

    # nx.draw(g, pos, with_labels=True, font_size(8))
    plt.show()

if __name__ == '__main__':

    # chance card, community chest decks as specified on monopoly wikia
    # go at 0
    # illinois at 24
    # st charles at 11
    # U is nearest utility
    # R is nearest railroad
    # B is go back 3 spaces
    # reading railroad at 5
    # boardwalk is 39
    # jail at 10
    chance_deck = [0, 10, 11, 24, 39, 'R', 'U', 'B', 5, 'pass', 'pass', 'pass', 'pass', 'pass', 'pass', 'pass']
    community_deck = [0, 'pass', 'pass', 'pass', 'pass', 10, 'pass', 'pass', 'pass', 'pass', 'pass', 'pass', 'pass',
                      'pass', 'pass', 'pass']
    board = Board([7, 22, 36], [2, 17, 33], chance_deck, community_deck)

    times_landed_on_per_game = [[] for x in range(0, 40)]
    sum_tiles = 0
    print(times_landed_on_per_game)

    # generate 1000 game instances of 100 turns per game, single player
    for j in range(0, 100):
        player = Player(0)
        game = Game(shuffle_deck(chance_deck), shuffle_deck(community_deck))
        for i in range(0, 100):
            speed = 0
            player.just_set_free = False
            while (roll(player)):
                speed += 1
                if speed == 3:
                    player.in_jail = True
                    player.increment(10)
                    player.pos = 10
                    break
        for i, x in enumerate(player.times_landed_on):
            times_landed_on_per_game[i].append(x)
        sum_tiles += sum(player.times_landed_on)

    probability_list = [0] * 40
    for i, x in enumerate(times_landed_on_per_game):
        probability_list[i] = sum(x) / sum_tiles
    rounded = [float("{0:.5f}".format(x)) for x in probability_list]
    draw(rounded)
    print(rounded)
    print(sum(probability_list))
    print(probability_list[0])
    print(probability_list[1])
    print(probability_list[5])
    print(probability_list[15])
    print(probability_list[25])
    print(probability_list[35])
    print(probability_list[39])

