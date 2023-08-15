'''
Author:        James Parkington
Created Date:  9/14/2023
Modified Date: 9/14/2023

File containing the implementation of the Dagger class for representing 
chess positions in a chess game analysis tool.
'''

from   Parser    import *
from   Utilities import *
from   queue     import PriorityQueue
from   typing    import *
import numpy           as np
import pandas          as pd
import pyarrow.dataset as ds


class PositionNode:
    '''
    A wrapper class for chess positions in the priority queue.
    Allows comparison based on the calculated cost (loss function value) to prioritize positions in the search.

    Attributes:
        cost      (float) : The calculated cost (loss function value) for the chess position.
        game_data (dict)  : A dictionary representing a chess game position from the dataset.
    '''

    def __init__(self, cost, game_data):
        self.cost = cost
        self.game_data = game_data

    def __lt__(self, other):
        return self.cost < other.cost
        
class Dagger:
    '''
    The Dagger class leverages Dijkstra's algorithm to find the best line of 5 moves across multiple games
    based on the user's input position and preference (white or black wins). It starts the search by prioritizing
    games based on final_centipawn_value, then uses a loss function to guide the search by the progression
    of centipawn_value for the next 5 moves.

    Attributes:
        games_df              (pd.DataFrame) : A DataFrame containing chess games information.
        user_board_sum        (int)          : User's input board sum to match.
        user_centipawn_value  (int)          : User's input centipawn value to compare.
        user_preference       (str)          : User's preference ("white" or "black") to guide the search.
        result                ((List[dict])) : List of results containing the best line of 5 moves.

    Methods:
        __init__        : Initializes the object with the given user input and games DataFrame.
        loss_function   : Defines a loss function using L2 regularization.
        dijkstra_search : Implements Dijkstra's algorithm to search through the games.
        __call__        : Executes the search and optionally prints the result.

    Mathematics Background:
        The loss function used in this class is a combination of mean squared error (MSE) and L2 regularization (ridge regression).
        It guides the search towards the optimal chess positions and avoids overfitting.

        Loss Function:
            L(pred) = (pred - user_centipawn_value)² / depth + λ * ||pred||²

        Where:
        - pred represents the average predicted centipawn value for the next depth moves.
        - user_centipawn_value is the user-provided centipawn value.
        - depth is the number of moves considered in the loss function evaluation (e.g., 10).
        - λ is the regularization strength.
        - ||pred||² denotes the squared L2 norm of the predicted values.

        Dijkstra's Algorithm:
        The graph traversal is based on Dijkstra's algorithm, which finds the shortest path from the user's position to the target position.
        The algorithm maintains a priority queue of nodes, sorted by their distance from the start node (user's position).
        The loss function defines the "distance" between nodes, and Dijkstra's algorithm seeks to minimize this distance.

        The mathematical process is:
        1. Initialize best_line = [] and current_board_sum = user_board_sum.
        2. Repeat 5 times:
            a. For each position p with p.board_sum = current_board_sum:
                - Enqueue (p, cost(p)) into a priority queue Q, where cost(p) is calculated using the loss function.
            b. Dequeue the position with the lowest cost from Q, denoted as p_best.
            c. Append p_best to best_line and update current_board_sum = p_best.next_board_sum.

        The result, best_line, represents the best sequence of moves that minimize the cost, considering centipawn evaluations and user preference.

    Time Complexity:
        Loss Function Calculation: 
        The time complexity of the loss function is 𝒪(depth), where depth is the number of moves considered in the evaluation (e.g., 10). The 
        calculation involves iterating through the next depth moves to compute the average predicted centipawn value.

        Dijkstra's Algorithm (Adapted): 
        The time complexity of the adapted Dijkstra's algorithm is 𝒪(5 * m * log(m)), where m is the number of positions with the same board 
        sum. The algorithm repeats 5 times (for 5 moves), and within each iteration, it processes m matching positions using a priority queue (heap), 
        resulting in a log(m) time complexity for enqueue and dequeue operations.

        Therefore, the total time complexity of the algorithm is 𝒪(mlog(m)), as dictated by the dominated term in the Dijkstra's adaptation.
    '''

    def __init__(self, 
                 storage_directory    : str, 
                 user_parser          : Parser,
                 user_preference      : str   = "white",
                 lambda_reg           : float = 0.01):

        self.games                = self.read_entire_directory(storage_directory)
        self.user_parser          = user_parser
        self.user_preference      = user_preference
        self.lambda_reg           = lambda_reg
        self.results              = {i + 1: {} for i in range(5)}

        self.user_board_sum, self.user_centipawn_value, self.best_index = self.find_best_learning_moment()

    def find_best_learning_moment(self) -> Tuple[int, int]:
        '''
        Analyzes the Positions in the user-supplied Parser to find the best learning moment.
        The learning moment is characterized by the largest net change in centipawn value.

        Returns:
            board_sum        : The bitboard sum of the best learning moment.
            centipawn_value  : The centipawn value of the best learning moment.
        '''

        centipawn_values = np.array([position.centipawn_value for position in self.user_parser.positions])
        net_changes      = np.abs(np.diff(centipawn_values))
        best_index       = np.argmax(net_changes)

        return self.user_parser.positions[best_index].position.bitboard_integers, \
               self.user_parser.positions[best_index].centipawn_value,            \
               best_index

    def read_entire_directory(self, storage_directory: str):
        '''
        Read the entire directory of Parquet files within the specified storage directory.

        Arguments:
            storage_directory : Directory containing the partitions.
            columns           : List of columns to read (optional).

        Returns:
            DataFrame : Pandas DataFrame containing the data from all partitions.
        '''

        dataset = ds.dataset(storage_directory, format = "parquet")
        table = dataset.to_table()

        return table.to_pandas()

    def loss_function(self, 
                      game_row : pd.Series,
                      depth    : int = 10) -> float:
        '''
        Defines a loss function based on ridge regression (L2 regularization).
        The function captures the difference between the predicted value and the actual value,
        penalizing large coefficients to prevent overfitting.
        '''

        pred = 0

        for i in range(depth):
            pred += self.games.iloc[game_row.name + i]['centipawn_evaluation']

        if self.user_preference == "black":
            pred = -pred

        pred    /= depth
        mse_term = ((pred - self.user_centipawn_value) ** 2)
        reg_term = self.lambda_reg * (pred ** 2)
        return mse_term / depth + reg_term

    def dijkstra_search(self):
        '''
        Implements Dijkstra's algorithm to find the best match by traversing the graph of chess positions.
        The search is guided by a loss function, and the result is stored in the result attribute.
        '''

        current_board_sum = self.user_board_sum
        for i in range(5):
            queue = PriorityQueue()

            # Prioritize games based on final_centipawn_value with positions that match current_board_sum
            sorted_games = self.games[self.games['board_sum'] == current_board_sum] \
                               .sort_values(by        = 'final_centipawn_value', 
                                            ascending = (self.user_preference == "black"))

            # Enqueue matching positions with the associated cost using the QueueItem wrapper class
            for _, game_row in sorted_games.iterrows():
                cost = self.loss_function(game_row)
                queue.put(PositionNode(cost, game_row.to_dict()))

            # Process the queue to find the best next move
            best_item = queue.get()
            best_move = best_item.game_data

            # Create a Parser object using the pgn field of the best_move
            parser_obj = Parser(best_move['pgn'])
            ply_index = best_move['ply']

            # Store the Parser object and ply index for the move directly in self.results
            self.results[i + 1] = {'parser': parser_obj, 'ply': ply_index}
            
            # Update current_board_sum for the next iteration
            current_board_sum = self.games.iloc[best_move['ply'] + 1]['board_sum']

    def __call__(self):
        self.dijkstra_search()
        return self.results