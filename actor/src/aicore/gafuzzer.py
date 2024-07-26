# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_logger import logger
from aicore.aifuzzer import AIFuzzer
import random
import numpy as np


# evaluated_population is a tuple: (individual, fitness)
def selection(evaluated_population, tournament_size):
    competition = random.sample(evaluated_population, tournament_size)
    winner = min(competition, key=lambda individual: individual[1])[0]
    # Return a copy of the selected individual
    return winner

def crossover_real(parent1, parent2):
    random_ratio1 = random.random()
    random_ratio2 = random.random()
    p1 = np.array(parent1)
    p2 = np.array(parent2)
    offspring1 = p2 * random_ratio1 + (1 - random_ratio1) * p1
    offspring2 = p2 * random_ratio2 + (1 - random_ratio2) * p1

    return (offspring1.tolist(), offspring2.tolist())

def mutate_real(chromosome, random_min, random_max):
    prob = 1 / len(chromosome)
    for i in range(len(chromosome)):
        if random.random() < prob:
            new_c = random.randrange(random_min, random_max)
            chromosome[i] = new_c
    return chromosome

def create_random_real(random_min, random_max):
    return random.randrange(random_min, random_max)

class GAFuzzerRANSim(AIFuzzer):

    def __init__(self, num_pop, size_pop, tournament_size = 10, crossover_prob = 0.7, pop_min = 0, pop_max = 100):
        self.num_pop = num_pop
        self.size_pop = size_pop
        self.tournament_size = tournament_size
        self.crossover_prob = crossover_prob
        self.pop_min = pop_min
        self.pop_max = pop_max
        self.populations = self.create_populations()

    def create_populations(self):
        new_population = []
        for i in range(self.num_pop):
            pop_tmp = []
            for j in range(self.size_pop):
                new_pop = create_random_real(self.pop_min, self.pop_max)
                pop_tmp.append(new_pop)
            new_population.append(pop_tmp)
        return new_population

    ## output new populations
    def next_paras(self, fitness):
        new_population = []
        while len(new_population) < self.num_pop:
            # Selection
            offspring1 = selection(fitness, self.tournament_size)
            offspring2 = selection(fitness, self.tournament_size)

            # Crossover
            if random.random() < self.crossover_prob:
                (offspring1, offspring2) = crossover_real(offspring1, offspring2)

            # Mutation
            offspring1 = mutate_real(offspring1, self.pop_min, self.pop_max)
            offspring2 = mutate_real(offspring2, self.pop_min, self.pop_max)

            new_population.append(offspring1)
            new_population.append(offspring2)

        self.populations = new_population
        return new_population


