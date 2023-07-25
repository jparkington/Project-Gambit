# Progress Report for Project Gambit

## Introduction
- Introduction to Project Gambit, a chess analytics research project.
- Discussion on the interplay of chess and technology, and the opportunities for enhanced learning and competition.
- Explanation of the unique approach of Project Gambit in enhancing the learning experience of chess players.

## Centipawn Value: A Novel Measure
**Nelson**
- Definition of the centipawn value, a standard used in computer chess to quantify the advantage of a player.
- Detailed discussion on the relative nature of centipawn value, its sensitivity to the game context, and why it provides a more nuanced measure than traditional chess piece values.
- Analysis of how the metric offers a means to quantitatively assess player decisions and guide the development of alternative, more advantageous moves.

## Chess Concepts and Linear Algebra
**James**
- Presentation of the chessboard and moves as elements of graph theory, using nodes to represent board positions and edges to denote moves.
- Explanation of how the graph theoretical representation of chess naturally models the game as a Directed Acyclic Graph (DAG), with each unique game state forming a node and each legal move forming a directed edge.
- Discussion on the deep relationship between linear algebra and these graph representations, drawing parallels between the matrix structures in linear algebra and adjacency matrices in graph theory.
- Discussion of how the paper "DAG-Width and Parity Games" can provide insights into handling the complexity of the chess game tree, especially when it comes to exploring and structuring the vast space of possible chess positions.

## Minimizing the Loss of Centipawn Value: Methodology and Strategies
**Nelson** and **James**
- Introduction to the concept of a loss function, its role in optimization problems, and its specific formulation in the context of Project Gambit.
- Detailed discussion on how the loss function, designed with centipawn values, influences the graph traversal algorithm, leading to a directed search that aims to identify optimal moves.
- Explanation of how the methodology mirrors shortest path algorithms in graph theory.
- Reference to "DeepChess: End-to-End Deep Neural Network for Automatic Learning in Chess," highlighting how it can provide insights into the automatic learning of board evaluations and move generation, which can be valuable for guiding the traversal.

## Further Explorations and Applications
**Nice-to-Have**
- Exploration of potential future research directions, such as applying the concepts and methodologies of Project Gambit to other games or decision-making problems.
- Discussion on how advancements in AI and machine learning could be used to further refine the loss function, improve the search algorithm, or provide richer, more personalized feedback to players.

## Conclusion
- Summary of the innovative and mathematical aspects of Project Gambit.
- Reiteration of the potential impact of Project Gambit on enhancing the learning experience of chess players through targeted feedback.
- Reflection on the future directions and expansions of the project.

<br>

---
---

<br>

## Ideas from 7/20
- Centipawn values for each user position need to be evaluated first, in order to find the "interesting" ones (or nodes worth performing the tree search with a loss function on)
- **Question to Explore**: Is it more valuable to pick the $n$ "most interesting" positions and perform the pathfinding algorithm on those $n$ nodes, or to run the entire tree first, or alternatively run the tree on all of the nodes? What's the tradeoff of the time complexity across these 3 options?
- **Question to Explore**: How do we determine the proper depth to apply to the search (exploration vs. exploitation)? How do we prevent the algorithm from stopping the search too early (e.g. there's an incredibly valuable node 4 positions down the line that we failed to look at, because we thought our current node was "insightful")?
- $L(\theta) = (x_0 - x_1)^2 + \cdots + c_n$