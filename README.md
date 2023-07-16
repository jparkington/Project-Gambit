<!-- omit in toc -->
# Project Gambit

Project Gambit is a chess analytics research project that aims to enhance the learning experience of chess players by providing targeted feedback on their gameplay. Instead of simply matching the user's game to a database of Grandmaster-level games, Project Gambit aims to identify the critical points in the game where the user made a poor decision, and then provide them with alternative moves that would have been better.

<!-- omit in toc -->
## Table of Contents

- [Introduction](#introduction)
- [New Direction](#new-direction)
- [Research Topics](#research-topics)
  - [Loss Function](#loss-function)
  - [Graph Traversal](#graph-traversal)
  - [Centipawn Value as Weight](#centipawn-value-as-weight)
  - [Directed Acyclic Graph (DAG)](#directed-acyclic-graph-dag)
- [Updates to Project Scotch](#updates-to-project-scotch)
  - [Position Class](#position-class)
  - [Parser Class](#parser-class)
  - [Navigator Class](#navigator-class)
  - [New Class: Dagger](#new-class-dagger)
  - [Storage](#storage)
- [Academic Papers](#academic-papers)
- [Acknowledgements](#acknowledgements)


## Introduction

In the world of chess, a game steeped in strategy and intellect, the rise of technology has opened new avenues for learning and competition. Inspired by this technological revolution, Project Scotch, a passion project from our CS5001 class at the Roux Institute, was born. It offers users the ability to compare their games to a database of Grandmaster-level games, thereby learning stronger continuities and improving their gameplay. However, as with any technology, there is always room for improvement and optimization.


## New Direction

Project Gambit is pivoting from optimizing the Longest Common Sequence (LCS) algorithm to providing a more targeted and effective learning experience for the user. The new direction involves identifying critical points in a game where the user made a poor decision and then providing them with alternative moves that would have been better. This will be achieved by conducting a directed search through the 7 million chess positions in our database, guided by a loss function that prioritizes the positions with the highest centipawn values. The chess positions will be stored in a tree-like data structure, facilitating a directed search that starts at the root and follows the edges to explore the tree. This approach is akin to a graph traversal algorithm, a fundamental concept in graph theory and computer science.


## Research Topics

### Loss Function

The new implementation will involve a loss function that guides the graph traversal algorithm. The loss function will be determined by the centipawn values of the positions, with the goal of minimizing this cost function during the traversal. This approach is similar to a shortest path algorithm in graph theory, where the goal is to find the path from the start node to the end node that has the minimum total weight. Understanding the concept of loss functions is crucial in many areas of data science, especially in optimization problems and machine learning. In our case, the loss function will help us quantify the "cost" of a player's decisions, guiding the algorithm towards the most instructive positions.

### Graph Traversal

The directed search through the chess positions can be seen as a graph traversal algorithm. The chess positions, represented as nodes in a graph, will be traversed in a manner that minimizes the cost function, which is determined by the centipawn values of the positions. Graph traversal is a fundamental concept in computer science and data science, with applications in network analysis, pathfinding algorithms, and more. In the context of Project Gambit, understanding graph traversal will allow us to efficiently navigate through the vast space of possible chess positions.

### Centipawn Value as Weight

The centipawn values will be used as weights in the directed search. These weights will guide the search towards the positions with the highest centipawn values, which represent the best moves that the user could have made. The use of weights in graph theory allows us to assign importance or cost to different paths, which is a common practice in many data science applications such as network optimization, resource allocation, and machine learning algorithms. In our case, the centipawn values provide a quantitative measure of the quality of a chess position, guiding the search towards the most instructive positions.

### Directed Acyclic Graph (DAG)

The tree-like data structure used to store the chess positions can be seen as a Directed Acyclic Graph (DAG), where each node represents a board state and each edge represents a move. This structure naturally lends itself to a directed search, as the search can start at the root and follow the edges to explore the tree. Understanding the properties and applications of DAGs is important in many areas of data science, including causal inference, scheduling problems, and more. In the context of Project Gambit, a DAG provides a natural and efficient way to represent and navigate the game tree of chess.


## Updates to Project Scotch

### Position Class

The `Position` class represents a particular board configuration. To accommodate the new research topics, we could extend this class to include an additional attribute:

- `centipawn_value`: This attribute would store the centipawn value for the position, allowing the algorithm to quickly identify the best positions without having to calculate the centipawn value on the fly.
- `transitions`: This attribute could be a list of other `Position` objects, each representing a possible transition from the current position to another position. This would be useful for implementing the directed search and graph traversal.

### Parser Class

The `Parser` class is responsible for parsing PGN files and extracting the positions. To accommodate the new research topics, we could extend this class to also extract the centipawn values for each position. This would involve adding a new method for parsing these additional pieces of information from the PGN files.

### Navigator Class

The `Navigator` class is responsible for navigating through the positions in a game. To accommodate the new research topics, we could extend this class to also navigate through the results of the directed search. This would involve adding a new method for navigating through the alternative positions suggested by the directed search. Additionally, the tkinter implementation will need to be updated to display up to four alternative positions to the user.

### New Class: Dagger

Given the significant changes and the introduction of graph-based concepts, it might be beneficial to introduce a new class, `Dagger`. This class could encapsulate the directed graph structure of the game states and transitions, providing methods for adding nodes (positions), adding edges (transitions), and performing graph traversal. The graph traversal method could use the centipawn values as weights to guide the search towards the positions with the highest values. It's name is a play on DAG.

### Storage

The current partition Parquet directory organizes the data by `total_ply`. Given the new direction of the project, this organization might not be the most efficient. Instead, we could organize the data by centipawn value, which would allow the algorithm to quickly identify the best positions. This would involve updating the code that writes to and reads from the Parquet directory.


## Academic Papers

Here are some academic papers that could provide valuable insights into the new direction of the project:

1. David, O., Netanyahu, N., & Wolf, L. (2016). [DeepChess: End-to-End Deep Neural Network for Automatic Learning in Chess](http://arxiv.org/pdf/1711.09667). 
   
   This paper presents a novel approach to learning and decision making in the game of chess. The authors use a deep learning model to learn chess board evaluations and move generation, which could provide insights into both how to structure the learning process for our chess positions and how to generate moves based on the learned evaluations.

2. Helmstetter, B., & Cazenave, T. (2006). [A Graph-Based Approach for Chess Endgames](https://link.springer.com/chapter/10.1007/11874683_26). 
   
   This paper presents a graph-based approach to solving chess endgames. The authors use a directed acyclic graph to represent the game states and apply graph algorithms to find the best moves, which we could use to understand how to structure the chess positions as a graph and how to traverse this graph to find the best moves.

3. Kreutzer, S. (2006). [DAG-Width and Parity Games](http://web.comlab.ox.ac.uk/people/Stephan.Kreutzer/Publications/stacs06.pdf). 
   
   This paper discusses the use of Directed Acyclic Graphs (DAGs) in the context of parity games, which could be applicable to the tree-like structure of chess positions.


## Acknowledgements

This project is being developed by:

- Joseph Nelson Farrell
- James Parkington

Their work was shaped under the supervision of both [Professor Weston Viles](https://roux.northeastern.edu/people/weston-viles/) and [Professor Lindsay Jamieson](https://roux.northeastern.edu/people/lindsay-jamieson/) during class *5020 - Linear Algebra* at the **Roux Institute of Northeastern University**.