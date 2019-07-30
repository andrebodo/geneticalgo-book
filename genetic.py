import sys
import time
import random
import statistics

from enum import Enum
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
	Strategy = None

	def __init__(self, genes, fitness, strategy):
		self.Genes = genes
		self.Fitness = fitness
		self.Strategy = strategy

class Strategies(Enum):
	Create = 0,
	Mutate = 1,
	Crossover = 2

# _ indicates protected function
def _generate_parent(length, geneSet, get_fitness):
	genes = []
	while len(genes) < length:
		sampleSize = min(length - len(genes), len(geneSet))
		genes.extend(random.sample(geneSet, sampleSize))
	fitness = get_fitness(genes)
	return Chromosome(genes, fitness, Strategies.Create)

def _mutate(parent, geneSet, get_fitness):
	childGenes = parent.Genes[:]
	index = random.randrange(0, len(parent.Genes))
	newGene, alternate = random.sample(geneSet, 2)
	childGenes[index] = alternate \
		if newGene == childGenes[index] \
		else newGene
	fitness = get_fitness(childGenes)
	return Chromosome(childGenes, fitness, Strategies.Mutate)

def _mutate_custom(parent, custom_mutate, get_fitness):
	childGenes = parent.Genes[:]
	custom_mutate(childGenes)
	fitness = get_fitness(childGenes)
	return Chromosome(childGenes, fitness, Strategies.Mutate)

# Generate sucessively better gene squence and send to get_best
# using yield -> code does not run when function is called! instead it
# returns a generator object (single use iterable)
def _get_improvement(new_child, generate_parent, maxAge, poolSize, maxSeconds):
	startTime = time.time()
	parent = bestParent = generate_parent() # This refers to the value from the function passed as an arguement
	yield maxSeconds is not None and time.time() - startTime > maxSeconds, bestParent
	parents = [bestParent] # For crossover
	historicalFitnesses = [bestParent.Fitness] # List of fitnesses of the historical best parents

	# populate parents array by generating new random parents, and contunously replace parent with better children
	for _ in range(poolSize - 1):
		parent = generate_parent()
		if maxSeconds is not None and time.time() - startTime > maxSeconds:
			yield True, parent
		if parent.Fitness > bestParent.Fitness:
			yield False, parent
			bestParent = parent
			historicalFitnesses.append(parent.Fitness)
		parents.append(parent)
	lastParentIndex = poolSize - 1
	pindex = 1
	while True:
		if maxSeconds is not None and time.time() - startTime > maxSeconds:
			yield True, bestParent
		# select a different parent to be the current parent
		pindex = pindex - 1 if pindex > 0 else lastParentIndex
		parent = parents[pindex]

		# child = new_child(parent) # This refers to the value from the function passed as an arguement
		child = new_child(parent, pindex, parents)
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
				# parent = child # child becomes new parent if chance is high
				parents[pindex] = child #crossover
				continue
			# parent = bestParent # otherwise replace parent with best parent, reset age to 0 giving time to anneal
			parents[pindex] = bestParent #crossover
			parent.Age = 0
			continue
		if not child.Fitness > parent.Fitness:
			# same fitness
			child.Age = parent.Age + 1
			# parent = child
			parents[pindex] = child #crossover
			continue
		# parent = child
		parents[pindex] = child # crossover
		parent.Age = 0
		# when find child with fitness better than best parent, replace best parent, and append to historical fitnesses
		if child.Fitness > bestParent.Fitness:
			yield False, child
			bestParent = child
			historicalFitnesses.append(child.Fitness)



def get_best(get_fitness, targetLen, optimalFitness, geneSet, display, 
			custom_mutate = None, custom_create = None, maxAge = None,
			poolSize = 1, crossover = None, maxSeconds = None):

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
			return Chromosome(genes, get_fitness(genes), Strategies.Create)

	strategyLookup = {
		Strategies.Create: lambda p, i, o: fnGenerateParent(),
		Strategies.Mutate: lambda p, i, o: fnMutate(p),
		Strategies.Crossover: lambda p, i, o: _crossover(p.Genes, i, o, get_fitness, crossover, fnMutate, fnGenerateParent)
	}

	usedStrategies = [strategyLookup[Strategies.Mutate]]
	if crossover is not None:
		usedStrategies.append(strategyLookup[Strategies.Crossover])

		def fnNewChild(parent, index, parents):
			return random.choice(usedStrategies)(parent, index, parents)
	else:
		def fnNewChild(parent, index, parents):
			return fnMutate(parent)

	for timedOut, improvement in _get_improvement(fnNewChild, fnGenerateParent, maxAge, poolSize, maxSeconds):
		if timedOut:
			return improvement
		display(improvement)
		f = strategyLookup[improvement.Strategy]
		usedStrategies.append(f)
		if not optimalFitness > improvement.Fitness:
			return improvement

def _crossover(parentGenes, index, parents, get_fitness, crossover, mutate, generate_parent):
	donorIndex = random.randrange(0, len(parents))
	if donorIndex == index:
		donorIndex = (donorIndex + 1) % len(parents)
	childGenes = crossover(parentGenes, parents[donorIndex].Genes)
	if childGenes is None:
		# parent and donor are indsitingushable
		parents[donorIndex] = generate_parent()
		return mutate(parents[index])
	fitness = get_fitness(childGenes)
	return Chromosome(childGenes, fitness, Strategies.Crossover)
