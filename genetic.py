import sys
import time
import random
import statistics

from math import exp
from bisect import bisect_left

class Benchmark:
	@staticmethod
	def run(function):
		timings = []
		stdout = sys.stdout
		for i in range(100):
			sys.stdout = None
			startTime = time.time()
			function()
			seconds = time.time() - startTime
			sys.stdout = stdout
			timings.append(seconds)
			mean = statistics.mean(timings)
			if i == 1:
				print(f'Benchmarking\n')
			if i % 10 == 9:
				print(f'{1 + i} {mean:3.2f} {statistics.stdev(timings, mean):3.2f}')

class Chromosome:
	Genes = None
	Fitness = None
	Age = 0 # Track how many generations passed since last improvement

	def __init__(self, genes, fitness):
		self.Genes = genes
		self.Fitness = fitness

# _ indicates protected function
def _generate_parent(length, geneSet, get_fitness):
	genes = []
	while len(genes) < length:
		sampleSize = min(length - len(genes), len(geneSet))
		genes.extend(random.sample(geneSet, sampleSize))
	fitness = get_fitness(genes)
	return Chromosome(genes, fitness)

def _mutate(parent, geneSet, get_fitness):
	index = random.randrange(0, len(parent.Genes))
	childGenes = parent.Genes[:]
	newGene, alternate = random.sample(geneSet, 2)
	childGenes[index] = alternate \
		if newGene == childGenes[index] \
		else newGene
	fitness = get_fitness(childGenes)
	return Chromosome(childGenes, fitness)

def _mutate_custom(parent, custom_mutate, get_fitness):
	childGenes = parent.Genes[:]
	custom_mutate(childGenes)
	fitness = get_fitness(childGenes)
	return Chromosome(childGenes, fitness)

# Generate sucessively better gene squence and send to get_best
# using yield -> code does not run when function is called! instead it
# returns a generator object (single use iterable)
def _get_improvement(new_child, generate_parent, maxAge):
	parent = bestParent = generate_parent() # This refers to the value from the function passed as an arguement
	yield bestParent
	historicalFitnesses = [bestParent.Fitness] # List of fitnesses of the historical best parents

	while True:
		child = new_child(bestParent) # This refers to the value from the function passed as an arguement
		if parent.Fitness > child.Fitness:
			if maxAge is None:
				continue
			parent.Age += 1
			if maxAge > parent.Age:
				continue
			# Annealing - If child gene sequence is far away from the current best solution, give gene
			# high probabily of continuing, otherwise do something else (implementation specific)
			# get index location of the child.Fitness in the historicalFitness
			index = bisect_left(historicalFitnesses, child.Fitness, 0, len(historicalFitnesses)) 
			difference = len(historicalFitnesses) - index # Get proximity of best fitness
			proportionSimilar = difference / len(historicalFitnesses)
			if random.random() < exp(-proportionSimilar): # e^difference = scaled difference 0 to 1
				parent = child # child becomes new parent if chance is high
				continue
			parent = bestParent # otherwise replace parent with best parent, reset age to 0 giving time to anneal
			parent.Age = 0
			continue
		if not child.Fitness > bestParent.Fitness:
			# same fitness
			child.Age = parent.Age + 1
			parent = child
			continue
		yield child
		parent = child
		parent.Age = 0
		# when find child with fitness better than best parent, replace best parent, and append to historical fitnesses
		if child.Fitness > bestParent.Fitness:
			yield child
			bestParent = child
			historicalFitnesses.append(child.Fitness)



def get_best(get_fitness, targetLen, optimalFitness, geneSet, display, 
			custom_mutate = None, custom_create = None, maxAge = None):
	random.seed()

	if custom_mutate is None:
		def fnMutate(parent):
			return _mutate(parent, geneSet, get_fitness)
	else:
		def fnMutate(parent):
			return _mutate_custom(parent, custom_mutate, get_fitness)

	if custom_create is None:
		def fnGenerateParent():
			return _generate_parent(targetLen, geneSet, get_fitness)
	else:
		def fnGenerateParent():
			genes = custom_create()
			return Chromosome(genes, get_fitness(genes))

	for improvement in _get_improvement(fnMutate, fnGenerateParent, maxAge):
		display(improvement)
		if not optimalFitness > improvement.Fitness:
			return improvement
