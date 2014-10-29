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

import os
import time
from random import randint, random, sample, shuffle

# Constants
N = 8
BASE_PERM = range(1, N+1)
P_RECOMB = 1
P_MUTATION = 0.8
POPULATION_SIZE = 100
MAX_EVAL = 100000

# Global fitness evaluation count
EVAL_COUNT = 0

def initialize():
    """ Initialize the population with random shuffles of the base permutation 
    """
    population = []
    for i in range(POPULATION_SIZE):
        copy = list(BASE_PERM)
        shuffle(copy)
        population.append(copy)
    return population

def mutation(x):
    """ Perform a swap mutation of an individual with the mutation probability 
    """
    r = random()
    if (r < P_MUTATION):
        s = randint(0, N-1)
        while True:
            t = randint(0, N-1)
            if not t == s:
                break
        x[s], x[t] = x[t], x[s]

def parent_selection(pop):
    """ Select parents for crossover by picking the best 2 out of random 5 """
    S = sample(pop, 5)
    F = [fitness(x) for x in S]

    L = sorted((e, i) for i, e in enumerate(F))
    p1 = S[L[0][1]]
    p2 = S[L[1][1]]

    return p1, p2

def survival_selection(pop, offspring):
    """ Perform survival selection by discarding the worst 2 """
    joined = pop + offspring
    F = [fitness(x) for x in joined]

    L = sorted((e, i) for i, e in enumerate(F))
    newpop = []
    for i in range(POPULATION_SIZE):
        newpop.append(joined[L[i][1]])

    return newpop

def crossover(p1, p2):
    """ Perform crossover by random cut and crossfil. """
    s = random()
    if not (s < P_RECOMB):
        return p1, p2

    r = randint(1, N-1)
    seg1 = p1[:r]
    seg2 = p2[:r]

    off1 = list(seg1)
    off2 = list(seg2)

    for i in p2:
        if not i in off1:
            off1.append(i)

    for i in p1:
        if not i in off2:
            off2.append(i)

    return off1, off2

def fitness(x):
    """  Calculate fitness in phenotype space, by counting the number of 
    diagonal checks that can be done, and multiplying this by -1. """
    global EVAL_COUNT
    EVAL_COUNT += 1
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
                if ((x[idx_plus] == x[n] + m) or (x[idx_plus] == x[n] - m)):
                    checks += 1
            if use_min:
                if ((x[idx_min] == x[n] + m) or (x[idx_min] == x[n] - m)):
                    checks += 1
    return checks/2

def have_solution(population):
    """ Check if a solution (0 checks) exists in the population. """
    return any((fitness(x) == 0 for x in population))

def main():
    """ Main loop, run until a solution is found or the maximum number of 
    fitness evaluations is performed. """
    global EVAL_COUNT
    population = initialize()

    it = 0
    while (not have_solution(population)) and (EVAL_COUNT < MAX_EVAL):
        print_status(population, it)
        p1, p2 = parent_selection(population)
        o1, o2 = crossover(p1, p2)
        mutation(o1)
        mutation(o2)
        population = survival_selection(population, [o1, o2])
        it += 1
    if EVAL_COUNT >= MAX_EVAL:
        print_status(population, it)
        print("Maximum number of fitness evaluations reached")
    if have_solution(population):
        print_status(population, it)
        s = next((x for x in population if fitness(x) == 0), None)
        print("Permutation representation: %s" % repr(s))
        if (it == 0):
            print("Found solution in initial population.")

#######################
# Auxiliary functions #
#######################

def print_status(pop, it):
    """ Print status line continuously to stdout, with best solution """
    global EVAL_COUNT
    txt = ""
    txt += "Running EA on %i-Queens problem\n" % N
    txt += "Generation: %i\tEvals: %i/%i\n" % (it, EVAL_COUNT, MAX_EVAL)

    F = [fitness(x) for x in pop]
    EVAL_COUNT -= len(pop)
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

def config_string(x):
    """ Construct a chess-board representation of a given permutation 
    representation """
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
