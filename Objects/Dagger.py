'''
Author:        James Parkington
Created Date:  9/14/2023
Modified Date: 9/14/2023

File containing the implementation of the Dagger class for representing 
chess positions in a chess game analysis tool.
'''

from   Parser    import *
from   Utilities import *
from   typing    import *
import heapq
import numpy           as np
import pandas          as pd
import pyarrow.dataset as ds
        
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
            L(pred) = Σ(pred - user_centipawn_value)² / depth + λ * ||pred||²

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
                 storage         : Utility, 
                 user_parser     : Parser,
                 user_preference : str   = "white",
                 lambda_reg      : float = 0.01):

        self.games                = self.read_entire_directory(storage.pq_path)
        self.user_parser          = user_parser
        self.user_preference      = user_preference
        self.lambda_reg           = lambda_reg
        self.results              = {i + 1: {} for i in range(5)}

        self.user_board_sum, self.user_centipawn, self.best_index = self.find_best_learning_moment()

    def find_best_learning_moment(self) -> Tuple[int, int]:
        '''
        Analyzes the Positions in the user-supplied Parser to find the best learning moment.
        The learning moment is characterized by the largest net change in centipawn value.

        Returns:
            board_sum : The bitboard sum of the best learning moment.
            centipawn : The centipawn value of the best learning moment.

        As a proof-of-concept, this function currently only looks through the first 12 ply of the sample game. This is because the
        `stockfish.get_evaluation()` function comingles centipawn value and "moves from checkmate", which is resulting in 
        inordinately large derivative values for some positions in the array.
        '''

        net_changes      = np.abs(np.diff(np.array([position.centipawn if position.centipawn else 0 for position in self.user_parser.positions[:12]])))
        best_index       = np.argmax(net_changes)

        return self.user_parser.positions[best_index].bitboard_integers, \
               self.user_parser.positions[best_index].centipawn,               \
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
                      row   : pd.Series,
                      depth : int = 10) -> float:
        '''
        Defines a loss function based on ridge regression (L2 regularization).
        The function captures the difference between the predicted value and the actual value,
        penalizing large coefficients to prevent overfitting.
        '''

        start_idx   = row.name
        pred_values = self.games.loc[start_idx : start_idx + depth - 1, 'centipawn_evaluation']
        pred        = np.mean(pred_values) * (1 if self.user_preference != "black" else -1)

        mse_term = ((pred - self.user_centipawn) ** 2)
        reg_term = self.lambda_reg * (pred ** 2)
        return mse_term / depth + reg_term

    # def dijkstra_search(self):
    #     '''
    #     Implements Dijkstra's algorithm to find the best match by traversing the graph of chess positions.
    #     The search is guided by a loss function, and the result is stored in the result attribute.
    #     '''

    #     current_board_sum = self.user_board_sum
    #     for i in range(5):
    #         # Filter games based on current_board_sum
    #         filtered_gamess = self.games[self.games['board_sum'] == current_board_sum]

    #         # Calculate cost for each row using apply method
    #         costs = filtered_gamess.apply(self.loss_function, axis = 1).values

    #         # Create a heap (priority queue) based on the calculated cost
    #         queue = [(cost, i) for i, cost in enumerate(costs)]
    #         heapq.heapify(queue)
    #         best_move = filtered_gamess.iloc[heapq.heappop(queue)[1]]

    #         # Create a Parser object using the pgn field of the best_move
    #         parser_obj = Parser(best_move['pgn'])
    #         ply_index = best_move['ply']

    #         # Store the Parser object and ply index for the move directly in self.results
    #         self.results[i + 1] = {'parser': parser_obj, 'ply': ply_index}
            
    #         # Update current_board_sum for the next iteration
    #         current_board_sum = self.games.iloc[best_move['ply'] + 1]['board_sum']

    def dijkstra_search(self):
        '''
        Implements Dijkstra's algorithm to find the best match by traversing the graph of chess positions.
        The search is guided by a loss function, and the result is stored in the result attribute.
        '''
        current_board_sum = self.user_board_sum

        for run in range(5):
            filtered_games = self.games[self.games['board_sum'] == current_board_sum].reset_index(drop=True)

            # Create a heap (priority queue) based on the calculated cost
            costs = filtered_games.apply(lambda row: self.loss_function(row), axis = 1)
            queue = list(zip(costs, filtered_games.index))
            heapq.heapify(queue)

            best_index = heapq.heappop(queue)[1]
            best_move  = filtered_games.iloc[best_index]

            # Create a Parser object using the pgn field of the best_move
            parser_obj = Parser(best_move['pgn'], False)
            ply_index  = best_move['ply']

            # Store the Parser object and ply index for the move directly in self.results
            self.results[run + 1] = {'parser': parser_obj, 'ply': ply_index}

            # Update current_board_sum for the next iteration
            next_board_sum_row = self.games[(self.games['ply'] == best_move['ply'] + 1) & (self.games['game_id'] == best_move['game_id'])]
            current_board_sum  = next_board_sum_row['board_sum'].iloc[0]

        return self.results

    def __call__(self):
        self.dijkstra_search()
        return self.best_index, self.results