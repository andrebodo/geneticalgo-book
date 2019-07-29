# Ch 7 - Knights Problem
# The project for this chapter is to figure out the minimal number of chess knights necessary to attack every square on a
# chess board. This means our chessboard must be at least 3x4 for some number of knights to be able to attack all squares
# on the board because a knight can only attack certain squares relative to its own location:

import random
import unittest
import genetic

from datetime import datetime as dt

class Position:
	X = None
	Y = None

	def __init__(self, x, y):
		self.X = x
		self.Y = y

	def __str__(self):
		return f'{self.X},{self.Y}'

	def __eq__(self, other):
		return self.X == other.X and self.Y == other.Y

	def __hash__(self):
		return self.X * 1000 + self.Y


def get_attacks(location, boardWidth, boardHeight):
	return [i for i in set(
		Position(x + location.X, y + location.Y)
		for x in [-2, -1, 1, 2] if 0 <= x + location.X < boardWidth
		for y in [-2, -1, 1, 2] if 0 <= y + location.Y < boardHeight
		and abs(y) != abs(x)
		)]

# Assign a specific number of knights to unique board positions
def create(fnGetRandomPosition, expectedKnights):
	genes = [fnGetRandomPosition() for _ in range(expectedKnights)]
	return genes

def mutate(genes, boardWidth, boardHeight, allPositions, nonEdgePositions):
	count = 2 if random.randint(0, 10) == 0 else 1
	while count > 0:
		count -= 1
		# figure out which knights are attacking which squares. The array in the dictionary has each knight’s gene index
		positionToKnightIndexes = dict((p, []) for p in allPositions)
		for i, knight in enumerate(genes):
			for position in get_attacks(knight, boardWidth, boardHeight):
				positionToKnightIndexes[position].append(i)
		# list of indexes of knights whose attacks are all covered by some other knight 
		# and build a list of the squares that are not under attack.
		knightIndexes = set(i for i in range(len(genes)))
		unattacked = []
		for kvp in positionToKnightIndexes.items():
			if len(kvp[1]) > 1:
				continue
			if len(kvp[1]) == 0:
				unattacked.append(kvp[0])
				continue
			for p in kvp[1]:
				if p in knightIndexes:
					knightIndexes.remove(p)
		# build the list of locations from which the unattacked squares can be attacked.
		potentialKnightPositions = \
			[p for positions in 
			map(lambda x: get_attacks(x, boardWidth, boardHeight), unattacked)
			for p in positions if p in nonEdgePositions] \
				if len(unattacked) > 0 else nonEdgePositions
		# choose a gene (knight) to replace.
		geneIndex = random.randrange(0, len(genes)) \
			if len(knightIndexes) == 0 \
			else random.choice([i for i in knightIndexes])
		# replace that knight with one likely to improve fitness
		position = random.choice(potentialKnightPositions)
		genes[geneIndex] = position

class Board:
	
	def __init__(self, positions, width, height):
		board = [['.'] * width for _ in range(height)]

		for index in range(len(positions)):
			knightPosition = positions[index]
			board[knightPosition.Y][knightPosition.X] = 'N'

		self._board = board
		self._width = width
		self._height = height

	def print(self):
		# 0,0 prints bottom left
		for i in reversed(range(self._height)):
			print(f'{i}\t{" ".join(self._board[i])}')
		print(f' \t{" ".join(map(str, range(self._width)))}')

def display(candidate, startTime, boardWidth, boardHeight):
	timeDiff = dt.now() - startTime
	board = Board(candidate.Genes, boardWidth, boardHeight)
	board.print()

	print('{0}\n\t{1}\t{2}'.format(
		' '.join(map(str, candidate.Genes)),
		candidate.Fitness,
		str(timeDiff)
		))

def get_fitness(genes, boardWidth, boardHeight):
	attacked = set(pos
					for kn in genes
					for pos in get_attacks(kn, boardWidth, boardHeight))
	return len(attacked)

class KnightsTest(unittest.TestCase):

	# def test_3x4(self):
	# 	width = 4
	# 	height = 3
	# 	self.find_knight_positions(width, height, 6)

	# def test_8x8(self):
	# 	width = 8
	# 	height = 8
	# 	self.find_knight_positions(width, height, 14)

	def test_10x10(self):
		width = 10
		height = 10
		self.find_knight_positions(width, height, 22)

	def find_knight_positions(self, boardWidth, boardHeight, expectedKnights):
		startTime = dt.now()

		allPositions = [Position(x, y) for y in range(boardHeight) for x in range(boardWidth)]

		if boardWidth < 6 or boardHeight < 6:
			nonEdgePositions = allPositions
		else:
			nonEdgePositions = [i for i in allPositions if 0 < i.X < boardWidth - 1 and 0 < i.Y < boardHeight - 1]

		def fnDisplay(candidate):
			display(candidate, startTime, boardWidth, boardHeight)

		def fnGetFitness(genes):
			return get_fitness(genes, boardWidth, boardHeight)

		def fnGetRandomPosition():
			return random.choice(nonEdgePositions)

		def fnMutate(genes):
			mutate(genes, boardWidth, boardHeight, allPositions, nonEdgePositions)

		def fnCreate():
			return create(fnGetRandomPosition, expectedKnights)

		optimalFitness = boardWidth * boardHeight
		best = genetic.get_best(fnGetFitness, None, optimalFitness, None, fnDisplay, fnMutate, fnCreate)
		self.assertTrue(not optimalFitness > best.Fitness)