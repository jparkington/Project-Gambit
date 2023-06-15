<!-- omit in toc -->
# Project Gambit

Project Gambit is a chess analytics research project that aims to optimize the Longest Common Sequence (LCS) algorithm used in [Project Scotch](https://github.com/jparkington/Project-Scotch) by incorporating concepts from **linear algebra**.

<!-- omit in toc -->
## Table of Contents

- [Introduction](#introduction)
- [Research Topics](#research-topics)
  - [Optimization of the LCS Algorithm](#optimization-of-the-lcs-algorithm)
  - [Markov Chains for Game State Transitions](#markov-chains-for-game-state-transitions)
  - [Probability Distributions for Chess Moves](#probability-distributions-for-chess-moves)
- [Academic Papers](#academic-papers)
- [Acknowledgements](#acknowledgements)

## Introduction

In chess, a gambit is a move in which a player sacrifices material with the hope of achieving a resulting advantageous position. Project Gambit embodies this idea, sacrificing the straightforward approach of the LCS algorithm for a more complex, but hopefully more effective, probabilistic approach. By integrating concepts from linear algebra, we aim to enhance the performance and accuracy of the LCS algorithm, providing users with more insightful and meaningful analysis of their chess games as our database of games scales.

## Research Topics

### Optimization of the LCS Algorithm

The LCS algorithm in Project Scotch is implemented in Cython for performance reasons. However, there might be further optimizations possible using Linear Algebra. 

One possibility may be to represent the sequences of positions as vectors and the LCS calculation as a matrix operation. This would involve modifying the `Position` class to include a vector representation of the position and the `Matcher` class to include a matrix representation of the LCS calculation. 

Another more applicable possibility is to use a heuristic to guide the LCS algorithm. This heuristic could be based on the transition probabilities in the Markov chain, favoring sequences of positions that are more likely according to the Markov chain.

### Markov Chains for Game State Transitions

In this area of research, we aim to model the transitions between different game states in a chess game using Markov chains. Each state represents a particular board configuration, and the transition probabilities are based on the frequency of transitions between states in our database of Grandmaster-level games.

In Project Scotch, the `Position` class represents a particular board configuration. This class could potentially be extended to include a `Transition` class that represents the transition from one position to another. We could represent these transitions with Markov chains, where each state is a `Position` and each transition is a `Transition`. 

The transition probabilities could then be calculated based on the frequency of transitions between states in the database of GM-level games. This would involve modifying the `Parser` class to extract not only the positions but also the transitions between positions from the PGN files. The `Matcher` class could then be modified to use the Markov chain to guide the LCS algorithm.

### Probability Distributions for Chess Moves

In Project Scotch, the `Position` class includes information about the legal moves from a position. This information could be used to construct a probability distribution for the moves from each position, based on the frequency of each move in the database of Grandmaster-level games. 

This would involve modifying the `Parser` class to extract not only the positions but also the moves from the PGN files. The `Matcher` class could then be modified to use these probability distributions to guide the LCS algorithm, favoring sequences of positions that are more likely according to the probability distributions.

## Academic Papers

1. [Combinatorial Game Theory](https://www.degruyter.com/document/doi/10.1515/9783110755411/html)
   - Discusses the application of game theory, including Markov Chains, in various board games. Could provide valuable insights into how to model game state transitions in chess.
   - *Jan. (2022). Combinatorial Game Theory. DOI: 10.1515/9783110755411*

2. [Aligning Superhuman AI with Human Behavior: Chess as a Model System](https://dl.acm.org/doi/10.1145/3394486.3403219)
   - This paper discusses how AI systems approach problems differently from humans and how modeling the granular actions that constitute human behavior can help bridge this gap. It uses chess as a model system and introduces Maia, a customized version of AlphaZero trained on human chess games. This paper could provide valuable insights into how to align the LCS algorithm with human behavior in chess.
   - *Reid McIlroy-Young, S. Sen, J. Kleinberg, Ashton Anderson (2020). Aligning Superhuman AI with Human Behavior: Chess as a Model System. DOI: 10.1145/3394486.3403219*

3. [Skill Rating by Bayesian Inference](https://www.researchgate.net/publication/224453252_Skill_Rating_by_Bayesian_Inference)
     - This paper discusses the rating systems used in chess and how they may be affected by varying rating distributions. While it does not delve into the specifics of probability distributions of chess moves or positions, it could provide a starting point for understanding how probability distributions could be applied to chess.
     - *Di Fatta, G., Haworth, G., and Regan, K. (2009). Rating systems with potentially varying rating distributions. DOI: 10.1109/CIDM.2009.4938653*

4. [Fast Evaluation of Sequence Pair in Block Placement by Longest Common Subsequence Computation](https://dl.acm.org/doi/10.1145/343647.343713)
     - This paper presents a new approach to evaluate a sequence pair based on comparing longest common subsequence in a pair of weighted sequences. It presents a very simple and efficient algorithm to solve the sequence pair evaluation problem. This could provide valuable insights into the efficiency and potential optimizations of the LCS algorithm.
     - The idea of pairing is an interesting, approachable optimization for chess specifically, since moves are comprised of 2 ply (a white move and a black move)
     - *Xiaoping Tang, Ruiqi Tian, Martin D. F. Wong (2001). Fast evaluation of sequence pair in block placement by longest common subsequence computation. DOI: 10.1145/343647.343713*

5. [A Space-Bounded Anytime Algorithm for the Multiple Longest Common Subsequence Problem](https://ieeexplore.ieee.org/document/6731533)
     - This paper formulates the MLCS problem into a graph search problem and presents two space-efficient anytime MLCS algorithms. The algorithms use an iterative beam widening search strategy to reduce space usage during the iterative process of finding better solutions. This could provide valuable insights into space-efficient implementations of the LCS algorithm.
     - *Jiaoyun Yang, Yun Xu, Yi Shang, Guoliang Chen (2014). A Space-Bounded Anytime Algorithm for the Multiple Longest Common Subsequence Problem. DOI: 10.1109/TKDE.2014.2304464*

## Acknowledgements

This project is being developed by:
- Joseph Nelson Farrell 
- James Parkington
  
Their work was shaped under the supervision of both [Professor Weston Viles](https://roux.northeastern.edu/people/weston-viles/) and [Professor Lindsay Jamieson](https://roux.northeastern.edu/people/lindsay-jamieson/) during class *5020 - Linear Algebra* at the **Roux Institute of Northeastern University**. 