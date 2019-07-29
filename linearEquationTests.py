import random
import unittest
import genetic
import fractions

from datetime import datetime as dt

class LinearEquationTests(unittest.TestCase):

	def test_4_unkowns(self):
		geneRange = [i for i in range(-13, 13) if i != 0]
		geneset = [i for i in set(
					fractions.Fraction(d, e)
					for d in geneRange
					for e in geneRange if e != 0)]

		def fnGenesToInputs(genes):
			return genes

		def e1(genes):
			x, y, z, a = genes
			return fractions.Fraction(1, 15) * x  - 2 * y  - 15 * z - fractions.Fraction(4, 5) * a - 3

		def e2(genes):
			x, y, z, a = genes
			return -fractions.Fraction(5, 2) * x - fractions.Fraction(9, 4) * y + 12 * z - a - 17

		def e3(genes):
			x, y, z, a = genes
			return -13 * x + fractions.Fraction(3, 10) * y - 6 * z - fractions.Fraction(2, 5) * a - 17

		def e4(genes):
			x, y, z, a = genes
			return fractions.Fraction(1, 2) * x + 2 * y + fractions.Fraction(7, 4) * z + fractions.Fraction(4, 3) * a + 9

		equations = [e1, e2, e3, e4]
		self.solve_unknowns(4, geneset, equations, fnGenesToInputs)

	# def test_3_unkowns(self):
	# 	geneRange = [i for i in range(-5, 5) if i != 0]
	# 	geneset = [i for i in set(
	# 				fractions.Fraction(d, e)
	# 				for d in geneRange
	# 				for e in geneRange if e != 0)]

	# 	def fnGenesToInputs(genes):
	# 		return genes

	# 	def e1(genes):
	# 		x, y, z = genes
	# 		return 6 * x - 2 * y + 8 * z - 20

	# 	def e2(genes):
	# 		x, y, z = genes
	# 		return y + 8 * x * z + 1

	# 	def e3(genes):
	# 		x, y, z = genes
	# 		return 2 * z * fractions.Fraction(6, x) + 3 * fractions.Fraction(y, 2) - 6

	# 	equations = [e1, e2, e3]
	# 	self.solve_unknowns(3, geneset, equations, fnGenesToInputs)


	# def test_2_unknowns(self):
	# 	geneset = [i for i in range(-5, 5) if i != 0]

	# 	def fnGenesToInputs(genes):
	# 		return genes[0], genes[1]

	# 	def e1(genes):
	# 		x, y = fnGenesToInputs(genes)
	# 		return x + 2 * y - 4

	# 	def e2(genes):
	# 		x, y = fnGenesToInputs(genes)
	# 		return 4 * x + 4 * y - 12

	# 	equations = [e1, e2]
	# 	self.solve_unknowns(2, geneset, equations, fnGenesToInputs)

	def solve_unknowns(self, numUnknowns, geneset, equations, fnGenesToInputs):
		startTime = dt.now()
		maxAge = 50

		window = Window(max(1, int(len(geneset) / (2 * maxAge))),
						max(1, int(len(geneset) / 3)),
						int(len(geneset) / 2))

		geneIndexes = [i for i in range(numUnknowns)]
		sortedGeneset = sorted(geneset)

		def fnDisplay(candidate):
			display(candidate, startTime, fnGenesToInputs)

		def fnGetFitness(genes):
			return get_fitness(genes, equations)

		def fnMutate(genes):
			mutate(genes, sortedGeneset, window, geneIndexes)

		optimalFitness = Fitness(0)
		best = genetic.get_best(fnGetFitness, numUnknowns, optimalFitness, geneset, fnDisplay, maxAge = maxAge)

		self.assertTrue(not optimalFitness > best.Fitness)

def get_fitness(genes, equations):
	fitness = Fitness(sum(abs(e(genes)) for e in equations))
	return fitness

def display(candidate, startTime, fnGenesToInputs):
	timeDiff = dt.now() - startTime
	symbols = 'xyza'
	result = ', '.join(f'{s} = {v}' for s, v in zip(symbols, fnGenesToInputs(candidate.Genes)))
	print(f'{result}\t{candidate.Fitness}\t{str(timeDiff)}')

class Fitness:

	TotalDifference = None

	def __init__(self, totalDifference):
		self.TotalDifference = totalDifference

	def __gt__(self, other):
		return self.TotalDifference < other.TotalDifference

	def __str__(self):
		return f'{float(self.TotalDifference):0.2f}'

class Window:
	Min = None
	Max = None
	Size = None

	def __init__(self, minimum, maximum, size):
		self.Min = minimum
		self.Max = maximum
		self.Size = size

	def slide(self):
		self.Size = self.Size - 1 if self.Size > self.Min else self.Max

def mutate(genes, sortedGeneset, window, geneIndexes):
	indexes = random.sample(geneIndexes, random.randint(1, len(genes))) \
		if random.randint(0, 10) == 0 else [random.choice(geneIndexes)]
	window.slide()
	while len(indexes) > 0:
		index = indexes.pop() # take next gene from indexes picked
		# calculate search bounds using window size, thus limiting number of genes to pick from
		genesetIndex = sortedGeneset.index(genes[index])
		start = max(0, genesetIndex - window.Size)
		stop = min(len(sortedGeneset) - 1, genesetIndex + window.Size)
		# Replace current gene with randomly picked one from new bounding range
		genesetIndex = random.randint(start, stop)
		genes[index] = sortedGeneset[genesetIndex]