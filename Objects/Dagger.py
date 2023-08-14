'''
Author:        James Parkington
Created Date:  9/14/2023
Modified Date: 9/14/2023

File containing the implementation of the Dagger class for representing 
chess positions in a chess game analysis tool.
'''

from   queue  import PriorityQueue
from   typing import *
import numpy  as np
import pandas as pd

class Dagger:
    '''
    The Dagger class leverages Dijkstra's algorithm to search through chess games to find the best match 
    based on a user's input position and preference (white or black wins). It starts the search by prioritizing
    games based on final_centipawn_value, then uses a loss function to guide the search by the progression
    of centipawn_value for the next 5 moves.

    Attributes:
        games_df              (pd.DataFrame) : A DataFrame containing chess games information.
        user_board_sum        (int)          : User's input board sum to match.
        user_centipawn_value  (int)          : User's input centipawn value to compare.
        user_preference       (str)          : User's preference ("white" or "black") to guide the search.
        result                (tuple)        : A tuple containing the best matching game_id, PGN string, and other details.

    Methods:
        __init__        : Initializes the object with the given user input and games DataFrame.
        loss_function   : Defines a loss function using L2 regularization.
        dijkstra_search : Implements Dijkstra's algorithm to search through the games.
        get_best_match  : Finds the best matching game based on the search results.
        __str__         : Returns a formatted string describing the best matching game.
        __call__        : Executes the search and optionally prints the result.

    Mathematics Background:
        The loss function used in this class is a combination of mean squared error (MSE) and L2 regularization (ridge regression).
        It guides the search towards the optimal chess positions and avoids overfitting.

        Loss Function:
            L(pred) = (pred - user_centipawn_value)² / n + λ * ||pred||²

        Where:
        - pred represents the predicted centipawn value for the next 5 moves.
        - user_centipawn_value is the user-provided centipawn value.
        - n is the number of moves considered (e.g., 5).
        - λ is the regularization strength.
        - ||pred||² denotes the squared L2 norm of the predicted values.

        Dijkstra's Algorithm:
        The graph traversal is based on Dijkstra's algorithm, which finds the shortest path from the user's position to the target position.
        The algorithm maintains a priority queue of nodes, sorted by their distance from the start node (user's position).
        The loss function defines the "distance" between nodes, and Dijkstra's algorithm seeks to minimize this distance.

        The algorithm's update step is expressed as:
            if dist[v] > dist[u] + weight(u, v):
                dist[v] = dist[u] + weight(u, v)

        Where:
        - u and v are nodes in the graph.
        - dist[u] and dist[v] are the current shortest distances from the start node to nodes u and v.
        - weight(u, v) is the "weight" of the edge from u to v, defined by the loss function.

        This mathematical formulation ensures that the search is directed towards the chess positions that best match the user's criteria,
        considering both the progression of centipawn values and the final centipawn value, based on user preference.
    '''

    def __init__(self, 
                 games_df             : pd.DataFrame, 
                 user_board_sum       : int, 
                 user_centipawn_value : int, 
                 user_preference      : str):

        self.games_df             = games_df
        self.user_board_sum       = user_board_sum
        self.user_centipawn_value = user_centipawn_value
        self.user_preference      = user_preference
        self.result               = (None, None, None, None)

    def loss_function(self, game_row: pd.Series) -> float:
        '''
        Defines a loss function based on ridge regression (L2 regularization).
        The function captures the difference between the predicted value and the actual value,
        penalizing large coefficients to prevent overfitting.
        '''

        pred = game_row['centipawn_evaluation']
        n = 5  # Considering the next 5 moves

        mse_term  = (pred - self.user_centipawn_value) ** 2 / n
        norm_term = self.λ * np.linalg.norm(pred) ** 2

        return mse_term + norm_term

    def dijkstra_search(self):
        '''
        Implements Dijkstra's algorithm to find the best match by traversing the graph of chess positions.
        The search is guided by a loss function, and the result is stored in the result attribute.
        '''
        # Initialize the priority queue
        queue = PriorityQueue()

        # Prioritize games based on final_centipawn_value
        sorted_games = self.games_df.sort_values(by = 'final_centipawn_value', ascending = (self.user_preference == "black"))

        # Enqueue initial matching positions with the associated cost
        for _, game_row in sorted_games.iterrows():
            if game_row['board_sum'] == self.user_board_sum:
                cost = self.loss_function(game_row)
                queue.put((cost, game_row))

        # Process the queue to find the best match
        best_sequence = None
        best_cost     = float('inf')

        while not queue.empty():
            cost, game_row = queue.get()
            game_id        = game_row['game_id']

            # Traverse next 5 moves
            for i in range(1, 6):
                next_row = self.games_df.iloc[game_row.name + i]
                cost    += self.loss_function(next_row)

            # Update best match if a better one is found
            if cost < best_cost:
                best_cost     = cost
                best_sequence = game_id, game_row['pgn'], cost

        self.result = best_sequence

    def get_best_match(self) -> Tuple[Optional[int], Optional[str], Optional[float]]:
        return self.result

    def __str__(self) -> str:
        result_info = self.result
        if not result_info[0]:
            return "No matching games found."

        return (f"Your best match is game ID {result_info[0]} with PGN: {result_info[1]}.\n"
                f"The sequence has a cost of {result_info[2]}.")

    def __call__(self):
        self.dijkstra_search()
        print(self)
        return self.get_best_match()