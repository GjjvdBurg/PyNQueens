#!/usr/bin/env python

"""
Author: Gertjan van den Burg
License: GNU GPL v2 (see LICENSE)

n-Queens problem EA

Representation      Permutation
Recombination       "Cut-and-crossfill" crossover
Recombination prob  100%
Mutation            Swap
Mutation prob       80%
Parent selection    Best 2 out of random 5
Survival selection  Replace worst
Population size     100
Number of offspring 2
Initialization      Random
Termination cond.   Solution or max. fitness evaluations

After A.E. Eiben and J.E. Smith (2007).

"""

from __future__ import print_function

import argparse
import os
import time

from random import randint, random, sample, shuffle

# Constants
N = 8
P_RECOMB = 1
P_MUTATION = 0.8
POPULATION_SIZE = 100
MAX_EVAL = 10000

class Individual(object):
    def __init__(self, perm=None):
        self.x = perm
        self._fitness = self.calculate_fitness()
    @property
    def fitness(self):
        return self._fitness
    def update(self):
        self._fitness = self.calculate_fitness()
    def __iter__(self):
        return iter(self.x)
    def __repr__(self):
        return repr(self.x)
    def calculate_fitness(self):
        # Calculate fitness in phenotype space
        N = len(self.x)
        checks = 0
        for n in range(N):
            for j in range(2, N):
                m = j - 1
                idx_plus = n + m
                idx_min = n - m
                use_plus = (0 <= idx_plus <= N-1)
                use_min = (0 <= idx_min <= N-1)
                if not (use_plus or use_min):
                    continue
                if use_plus:
                    if ((self.x[idx_plus] == self.x[n] + m) or 
                            (self.x[idx_plus] == self.x[n] - m)):
                        checks += 1
                if use_min:
                    if ((self.x[idx_min] == self.x[n] + m) or 
                            (self.x[idx_min] == self.x[n] - m)):
                        checks += 1
        return checks/2

class Population(object):
    def __init__(self, pop_size=POPULATION_SIZE, nqueens=N,
            p_mutate=P_MUTATION, p_recomb=P_RECOMB, max_eval=MAX_EVAL):
        self.population = []
        self.pop_size = pop_size
        self.nqueens = nqueens
        self.prob_mutation = p_mutate
        self.prob_recomb = p_recomb
        self.eval_count = 0
        self.max_eval = max_eval

        self.initialize_population()

    def initialize_population(self):
        # Initialize the population with random shuffles of the base permutation 
        for i in range(self.pop_size):
            copy = list(range(1, self.nqueens+1))
            shuffle(copy)
            ind = Individual(copy)
            self.population.append(ind)
            self.eval_count += 1

    def mutate(self, ind):
        # Perform swap mutation of an individual with the mutation probability
        r = random()
        if r < self.prob_mutation:
            s = randint(0, self.nqueens - 1)
            t = randint(0, self.nqueens - 1)
            while s == t:
                t = randint(0, self.nqueens - 1)
            ind.x[s], ind.x[t] = ind.x[t], ind.x[s]
        ind.update()
        self.eval_count += 1

    def parent_selection(self):
        # Select parents for crossover by picking the best 2 out of random 5
        S = sample(self.population, 5)
        F = [x.fitness for x in S]
        L = sorted((e, i) for i, e in enumerate(F))
        p1 = S[L[0][1]]
        p2 = S[L[1][1]]
        return p1, p2

    def survival_selection(self, offspring):
        # Perform survival selection by discarding the worst 2
        joined = self.population + offspring
        F = [x.fitness for x in joined]
        L = sorted((e, i) for i, e in enumerate(F))
        newpop = []
        for i in range(self.pop_size):
            newpop.append(joined[L[i][1]])
        self.population = newpop

    def crossover(self, p1, p2):
        s = random()
        if not (s < self.prob_recomb):
            return p1, p2
        r = randint(1, N-1)
        seg1 = p1.x[:r]
        seg2 = p2.x[:r]
        off1 = list(seg1)
        off2 = list(seg2)
        for i in p2:
            if not i in off1:
                off1.append(i)
        for i in p1:
            if not i in off2:
                off2.append(i)
        ind1 = Individual(off1)
        ind2 = Individual(off2)
        self.eval_count += 2
        return ind1, ind2

    def have_solution(self):
        return any((x.fitness == 0 for x in self.population))

    def evolve(self):
        it = 0
        while (not self.have_solution()) and (self.eval_count < self.max_eval):
            print_status(self, it)
            p1, p2 = self.parent_selection()
            o1, o2 = self.crossover(p1, p2)
            self.mutate(o1)
            self.mutate(o2)
            self.survival_selection([o1, o2])
            it += 1
        if self.eval_count >= self.max_eval:
            print_status(self, it)
            print("Maximum number of fitness evaluations reached")
        if self.have_solution():
            print_status(self, it)
            s = next((x for x in self.population if x.fitness == 0), None)
            print("Permutation representation: %s" % repr(s))

def main():
    p = Population()
    p.evolve()

#######################
# Auxiliary functions #
#######################

def print_status(population, it):
    """ Print status line continuously to stdout, with best solution """
    pop = population.population
    txt = ""
    txt += "Running EA on %i-Queens problem\n" % N
    txt += "Generation: %i\tEvals: %i/%i\n" % (it, population.eval_count, 
            population.max_eval)

    F = [x.fitness for x in pop]
    L = sorted((e, i) for i, e in enumerate(F))
    mean_fitness = float(sum(F))/float(len(F))
    mean_variance = (float(sum((float(f)**2.0 for f in F)))/float(len(F)) - 
            mean_fitness**2.0)
    txt += ("Population statistics: mean = %3.3f\tvariance = %3.3f\n\n" % 
            (mean_fitness, mean_variance))

    best_idx = L[0][1]
    best_indiv = pop[best_idx]
    best_fit = F[best_idx]
    txt += "Current best solution (fitness = %i):\n" % best_fit
    txt += config_string(best_indiv)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(txt, end='\r')
    time.sleep(.1)

def config_string(ind):
    """ Construct a chess-board representation of a given permutation 
    representation """
    x = ind.x
    txt = "\n"
    if (N > 9):
        txt += " "
    txt += "    "
    if (N > 9):
        for i in range(1, N+1):
            if (i < 10):
                txt += "%i  " % i
            else:
                txt += "%i " % i
    else:
        for i in range(1, N+1):
            txt += "%i  " % i
    txt += "\n"
    if (N > 9):
        txt += " "
    txt += "   _" + "_".join(["__" for i in range(N)]) + "\n"
    for i in range(N):
        if (N < 10):
            txt += "%i |" % (i + 1)
        else:
            txt += " %i |" % (i + 1) if i < 9 else "%i |" % (i+1)
        for j in range(N):
            if x[j] == i+1:
                txt += " x "
            else:
                txt += " - "
        txt += "|\n"
    txt += "   _" + "_".join(["__" for i in range(N)]) + "\n"
    txt += "\n"
    return txt

if __name__ == '__main__':
    start_t = os.times()
    main()
    end_t = os.times()
    print("Total running time: %4.4f seconds" % (end_t[-1] - start_t[-1]))
