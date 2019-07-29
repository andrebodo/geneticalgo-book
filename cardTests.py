import unittest
import genetic
import operator
import functools
import random

from datetime import datetime as dt

# Card Problem:
# Ace, 2 - 10 cards given
# Separate into 2 groups of 5
# One group must have a product of 360
# Other group sums to 36

class CardTests(unittest.TestCase):

	def test(self):
		geneset = [i + 1 for i in range(10)] #Ace, 2 - 10
		startTime = dt.now()

		def fnDisplay(candidate):
			display(candidate, startTime)

		def fnGetFitness(genes):
			return get_fitness(genes)

		def fnMutate(genes):
			mutate(genes, geneset)

		optimalFitness = Fitness(36, 360, 0)
		best = genetic.get_best(fnGetFitness, 10, optimalFitness, geneset, fnDisplay, custom_mutate = fnMutate)

		self.assertTrue(not optimalFitness > best.Fitness)


def get_fitness(genes):
	group1Sum = sum(genes[0:5]) 
	group2Prod = functools.reduce(operator.mul, genes[5:10])
	duplicateCount = len(genes) - len(set(genes)) # Count the number of duplicates -> set() will not contain duplicates
	return Fitness(group1Sum, group2Prod, duplicateCount)

class Fitness:
	Group1Sum = None
	Group2Prod = None
	TotalDifference = None
	DuplicateCount = None

	def __init__(self, group1Sum, group2Prod, duplicateCount):
		self.Group1Sum = group1Sum
		self.Group2Prod = group2Prod
		sumDifference = abs(36 - group1Sum)
		prodDifference =abs(360 - group2Prod)
		self.TotalDifference = sumDifference + prodDifference
		self.DuplicateCount = duplicateCount

	def __gt__(self, other):
		if self.DuplicateCount != other.DuplicateCount:
			return self.DuplicateCount < other.DuplicateCount
		return self.TotalDifference < other.TotalDifference

	def __str__(self):
		return f'sum: {self.Group1Sum} prod: {self.Group2Prod} dups: {self.DuplicateCount}'

def display(candidate, startTime):
	timeDiff = dt.now() - startTime
	print("{0} : {1}\t{2}\t{3}".format(
		', '.join(map(str, candidate.Genes[0:5])),
		', '.join(map(str, candidate.Genes[5:10])),
		candidate.Fitness,
		str(timeDiff)
		))

def mutate(genes, geneset):
	if len(genes) == len(set(genes)): # If there are no duplicates, swap genes a random number of times
		count = random.randint(1, 5)
		while count > 0:
			count -= 1
			indexA, indexB = random.sample(range(len(genes)), 2)
			genes[indexA], genes[indexB] = genes[indexB], genes[indexA]
	else: # Change 1 random gene if there are duplicates
		indexA = random.randrange(0, len(genes))
		indexB = random.randrange(0, len(geneset))
		genes[indexA] = geneset[indexB]