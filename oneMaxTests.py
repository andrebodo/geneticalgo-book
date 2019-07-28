import time
import unittest
from . import genetic


def get_fitness(genes):
	return genes.count(1)

def display(candidate, startTime):
	timeDiff = time.time() - startTime
	print('{0}...{1}\t{2:3.2f}\t{3}'.format(
		''.join(map(str, candidate.Genes[:15])),
		''.join(map(str, candidate.Genes[-15:])),
		candidate.Fitness,
		str(timeDiff)
		))

class OneMaxTests(unittest.TestCase):
	def test(self, length = 100):

		startTime = time.time()
		geneset = [0, 1]

		def fnDisplay(candidate):
			display(candidate, startTime)

		def fnGetFitness(genes):
			return get_fitness(genes)

		optimalFitness = length
		best = genetic.get_best(fnGetFitness, length, optimalFitness, geneset, fnDisplay)
		self.assertEqual(best.Fitness, optimalFitness)

	def test_benchmark(self):
		genetic.Benchmark.run(lambda: self.test(4000))

if __name__ == '__main__':
	unittest.main()