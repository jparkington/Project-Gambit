<!-- omit in toc -->
# Project Gambit

Project Gambit is a chess analytics research project that aims to enhance the learning experience of chess players by providing targeted feedback on their gameplay. Instead of simply matching the user's game to a database of Grandmaster-level games, Project Gambit aims to identify the critical points in the game where the user made a poor decision, and then provide them with alternative moves that would have been better.

<!-- omit in toc -->
## Table of Contents

- [Introduction](#introduction)
- [New Direction](#new-direction)
- [Research Topics](#research-topics)
  - [Centipawn Regression](#centipawn-regression)
  - [Directed Search with Loss Function](#directed-search-with-loss-function)
  - [Changes to Project Scotch Implementation](#changes-to-project-scotch-implementation)
- [Academic Papers](#academic-papers)
- [Acknowledgements](#acknowledgements)

## Introduction

In the world of chess, a game steeped in strategy and intellect, the rise of technology has opened new avenues for learning and competition. Inspired by this technological revolution, Project Scotch, a passion project from our CS5001 class at the Roux Institute, was born. It offers users the ability to compare their games to a database of Grandmaster-level games, thereby learning stronger continuities and improving their gameplay. However, as with any technology, there is always room for improvement and optimization.

## New Direction

After careful consideration and consultation with our professor, we've decided to pivot the focus of the project from optimizing the Longest Common Sequence (LCS) algorithm to providing a more targeted and effective learning experience for the user. The new direction of the project involves using a centipawn regression as a target variable to understand the quality of the user's moves. This would allow us to identify the critical points in the game where the user made a poor decision, and then provide them with alternative moves that would have been better. We also plan to provide multiple game options for each learning opportunity, allowing the user to see a variety of different strategies and responses to a given situation.

## Research Topics

### Centipawn Regression

The centipawn regression will be used to identify the critical points in the game where the user made a poor decision. This will involve calculating the centipawn value for each record in the database ahead of time, allowing the algorithm to quickly identify the critical points in the game without having to calculate the centipawn value on the fly.

### Directed Search with Loss Function

We plan to use a directed search with a loss function to quickly identify the best positions for the user to learn from. This approach will allow us to traverse the 7 million positions in our database in a more efficient manner than the current implementation, which has a time complexity of n^2. The loss function will guide the search towards the positions with the highest centipawn values, which represent the best moves that the user could have made.

### Changes to Project Scotch Implementation

To implement these new research topics, several changes will need to be made to the Project Scotch implementation. First, the database will need to be updated to include the centipawn value for each position. This will allow the algorithm to quickly identify the best positions without having to calculate the centipawn value on the fly. Second, the search algorithm will need to be updated to use a directed search with a loss function, which will guide the search towards the positions with the highest centipawn values. Finally, the user interface will need to be updated to display multiple game options for each learning opportunity, allowing the user to see a variety of different strategies and responses to a given situation.

## Academic Papers

Here are some academic papers that could provide valuable insights into the new direction of the project:

1. ["Deep Learning for Load Forecasting: Sequence to Sequence Recurrent Neural Networks With Attention"](https://dx.doi.org/10.1109/ACCESS.2020.2975738) by Ljubisa Sehovac and Katarina Grolinger. [PDF Link](https://ieeexplore.ieee.org/ielx7/6287639/8948470/09006868.pdf)

2. ["A Theoretical Insight Into the Effect of Loss Function for Deep Semantic-Preserving Learning"](https://dx.doi.org/10.1109/TNNLS.2021.3090358) by A. Akbari et al. [PDF Link](https://openresearch.surrey.ac.uk/view/delivery/44SUR_INST/12150818710002346/13150818700002346)

3. ["Forecasting Volatility of Stock Index: Deep Learning Model with Likelihood-Based Loss Function"](https://dx.doi.org/10.1155/2021/5511802) by Fang Jia and Boli Yang. [PDF Link](https://downloads.hindawi.com/journals/complexity/2021/5511802.pdf)

## Acknowledgements

This project is being developed by:

- Joseph Nelson Farrell
- James Parkington

Their work was shaped under the supervision of both Professor Weston Viles and Professor Lindsay Jamieson during class 5020 - Linear Algebra at the Roux Institute of Northeastern University.
