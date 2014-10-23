PyNQueens
=========

A Python implementation of a simple Evolutionary Algorithm solver for the 
N-Queens problem.

*Author: Gertjan van den Burg*

To run the program simply run:

    python nqueens.py


This program is an implementation of the EA strategy for the 8-queens problem 
as described on page 27 of A.E. Eiben and J.E. Smith (2007).

Interesting parameters to play with (see under *Constants*):

**N:** Number of queens on the board

**P_RECOMB:** Recombination probability

**P_MUTATION:** Mutation probability

**POPULATION_SIZE:** Size of the population (number of individuals in the 
solution pool)

**MAX_EVAL:** Maximum number of fitness evaluations to do (stopping criterium)
