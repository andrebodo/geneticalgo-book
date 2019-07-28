import random
import time
#from pip import __main__
import unittest
from . import genetic

# Fitness fucntion - Total number of letters matching in same position
def get_fitness(genes, target):
	return sum(1 for expected, actual in zip(target, genes) if expected == actual)

# # Display 
def display(candidate, startTime):
	timeDiff = time.time() - startTime
	print(f'{candidate.Genes}\t{candidate.Fitness}\t{str(timeDiff)}')

class GuessPasswordTest(unittest.TestCase):

	geneset = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!."

	def test_Hello_World(self):
		target = 'Hello World!'
		self.guess_password(target)

	def test_For_I_am_fearfully_and_wonderfully_made(self):
		target = "For I am fearfully and wonderfully made."
		self.guess_password(target)

	def test_Random(self):
		length = 250
		target = ''.join(random.choice(self.geneset) for _ in range(length))
		self.guess_password(target)

	def test_benchmark(self):
		genetic.Benchmark.run(self.test_Random)
		#genetic.Benchmark.run(self.test_For_I_am_fearfully_and_wonderfully_made)

	def guess_password(self, target):
		startTime = time.time()

		def fnGetFitness(genes):
			return get_fitness(genes, target)

		def fnDisplay(candidate):
			display(candidate, startTime)		

		optimalFitness = len(target)
		best = genetic.get_best(fnGetFitness, len(target), optimalFitness, self.geneset, fnDisplay)

		self.assertEqual(best.Genes, target)

if __name__ == '__main__':
	unittest.main() # Will call each function who name starts with test

# python -m unittest guessPasswordTest # Add -b for silent output