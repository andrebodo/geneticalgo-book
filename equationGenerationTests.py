# genetic programming -> overlay grammer on genes which may or may not include embedded data
# the operation-genes can be evaluated to produce a result
import unittest
import genetic
import random

from datetime import datetime as dt

# problem-specific gene sequence treatment. 
# Apply operation genes to neighboring numbers, rolling up to get final result
def evaluate(genes, prioritizedOperations):
	equation = genes[:]
	for operationSet in prioritizedOperations:
		iOffset = 0
		for i in range(1, len(equation), 2):
			i += iOffset
			opToken = equation[i]
			if opToken in operationSet:
				leftOperand = equation[i - 1]
				rightOperand = equation[i + 1]
				equation[i - 1] = operationSet[opToken](leftOperand, rightOperand)
				del equation[i + 1]
				del equation[i]
				iOffset -= 2
	return equation[0]

# don’t know how many symbols needed to produce a particular result, and need to alternate numbers and operations.
def create(numbers, operations, minNumbers, maxNumbers):
	genes = [random.choice(numbers)]
	count = random.randint(minNumbers, 1 + maxNumbers)
	while count > 1:
		count -= 1
		genes.append(random.choice(operations))
		genes.append(random.choice(numbers))
	return genes

# append operation-number pair to gene sequence
def mutate(genes, numbers, operations, minNumbers, maxNumbers, fnGetFitness):
	count = random.randint(1, 10)
	initialFitness = fnGetFitness(genes)
	while count > 0:
		count -= 1
		if fnGetFitness(genes) > initialFitness:
			return
		numberCount = (1 + len(genes)) / 2
		# add operation-number pair
		appending = numberCount < maxNumbers and random.randint(0, 100) == 0
		if appending:
			genes.append(random.choice(operations))
			genes.append(random.choice(numbers))
			continue
		# remove opertaion-number pair
		removing = numberCount > minNumbers and random.randint(0, 20) == 0
		if removing:
			index = random.randrange(0, len(genes) - 1)
			del genes[index]
			del genes[index]
			continue
		# mutate and operation or number
		index = random.randrange(0, len(genes))
		genes[index] = random.choice(operations) if (index & 1) == 1 else random.choice(numbers)

def display(candidate, startTime):
	print(f'{" ".join(map(str, [i for i in candidate.Genes]))}\t{candidate.Fitness}\t{dt.now() - startTime}')

def get_fitness(genes, expectedTotal, fnEvaluate):
	result = fnEvaluate(genes)
	if result != expectedTotal:
		fitness = expectedTotal - abs(result - expectedTotal)
	else:
		fitness = 1000 - len(genes)
	return fitness

def add(a, b):
	return a + b

def subtract(a, b):
	return a - b

def multiply(a, b):
	return a * b

class EquationGenerationTests(unittest.TestCase):

	def test_addition(self):
		operations = ['+', '-']
		prioritizedOperations = [{'+':add, '-':subtract}]
		optimalLengthSolution = [7, '+', 7, '+', 7, '+', 7, '+', 7, '-', 6]
		self.solve(operations, prioritizedOperations, optimalLengthSolution)

	def test_multiplcation(self):
		operations = ['+', '-', '*']
		prioritizedOperations = [{'*':multiply}, {'+':add, '-':subtract}]
		optimalLengthSolution = [6, '*', 3, '*', 3, '*', 6, '-', 7]
		self.solve(operations, prioritizedOperations, optimalLengthSolution)			

	def test_exponent(self):
		operations = ['^', '+', '-', '*']
		prioritizedOperations = [{'^': lambda a, b: a ** b},
								 {'*':multiply},
								 {'+':add, '-':subtract}]
		optimalLengthSolution = [6, '^', 3, '*', 2, '-', 5]
		self.solve(operations, prioritizedOperations, optimalLengthSolution)					

	def test_benchmark(self):
		genetic.Benchmark.run(lambda: self.test_exponent())

	def solve(self, operations, prioritizedOperations, optimalLengthSolution):
		numbers = [1, 2, 3, 4, 5, 6, 7]
		expectedTotal = evaluate(optimalLengthSolution, prioritizedOperations)
		minNumbers = (1 + len(optimalLengthSolution)) / 2
		maxNumbers = 6 * minNumbers
		startTime = dt.now()

		def fnEvaluate(genes):
			return evaluate(genes, prioritizedOperations)

		def fnDisplay(candidate):
			display(candidate, startTime)

		def fnGetFitness(genes):
			return get_fitness(genes, expectedTotal, fnEvaluate)
		
		def fnCreate():
			return create(numbers, operations, minNumbers, maxNumbers)
		
		def fnMutate(child):
			mutate(child, numbers, operations, minNumbers, maxNumbers, fnGetFitness)

		optimalFitness = fnGetFitness(optimalLengthSolution)
		best = genetic.get_best(fnGetFitness, None, optimalFitness, None, fnDisplay, fnMutate, fnCreate, maxAge=50)
		self.assertTrue(not optimalFitness > best.Fitness)

