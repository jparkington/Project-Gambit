# Project Gambit

Project Gambit is an innovative chess analytics tool that aims to optimize the Longest Common Sequence (LCS) algorithm used in [Project Scotch](https://github.com/jparkington/Project-Scotch) by incorporating concepts from **linear algebra**.

## Introduction

In chess, a gambit is a move in which a player sacrifices material with the hope of achieving a resulting advantageous position. Project Gambit embodies this idea, sacrificing the straightforward approach of the LCS algorithm for a more complex, but hopefully more effective, probabilistic approach. By integrating concepts from linear algebra, we aim to enhance the performance and accuracy of the LCS algorithm, providing users with more insightful and meaningful analysis of their chess games as its database scales.

## Research Topics

### Optimization of the LCS Algorithm

The LCS algorithm is a crucial component of Project Scotch, but its performance can be improved. In this research topic, we explore how Linear Algebra can be used to optimize the LCS algorithm. This could involve using matrix operations to speed up the calculation of the LCS or developing new methods to guide the LCS algorithm more effectively.

### Markov Chains for Game State Transitions

In this area of research, we aim to model the transitions between different game states in a chess game using Markov chains. Each state represents a particular board configuration, and the transition probabilities are based on the frequency of transitions between states in our database of Grandmaster-level games. By analyzing the Markov chain, we hope to gain insights into the dynamics of the game and improve the performance of the LCS algorithm.

### Probability Distributions for Chess Moves

This research topic involves constructing probability distributions for different chess moves based on our database of Grandmaster-level games. These distributions can then be analyzed using concepts from Linear Algebra, such as limiting behavior, to study the long-term trends in the use of different moves. This could provide valuable insights that could be used to enhance the LCS algorithm.

## Acknowledgements

This project is being developed by:
- Joseph Nelson Farrell 
- James Parkington
  
Their work was shaped under the supervision of both [Professor Weston Viles](https://roux.northeastern.edu/people/weston-viles/) and [Professor Lindsay Jamieson](https://roux.northeastern.edu/people/lindsay-jamieson/) during class *5020 - Linear Algebra* at the **Roux Institute of Northeastern University**. 