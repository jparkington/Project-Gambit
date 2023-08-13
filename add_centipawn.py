from concurrent.futures import ProcessPoolExecutor
from io                 import StringIO
from pathlib            import Path
from shutil             import copyfile
from stockfish          import Stockfish
from typing             import List, Tuple
import chess.pgn
import os
import pandas as pd

def evaluate_game(game_id        : int, 
                  game_pgn       : str, 
                  stockfish_path : str, 
                  depth          : int) -> List[Tuple[int, int, int, int]]:
    
    stockfish            = Stockfish(path=stockfish_path, depth=depth)
    pgn_io               = StringIO(game_pgn)
    game                 = chess.pgn.read_game(pgn_io)
    evaluations          = []
    board                = game.board()
    previous_evaluation  = None

    for move in game.mainline_moves():
        board.push(move)
        stockfish.set_fen_position(board.fen())
        centipawn_evaluation = stockfish.get_evaluation()['value']
        centipawn_diff = abs(centipawn_evaluation - previous_evaluation) if previous_evaluation is not None else 0
        evaluations.append((game_id, board.ply(), centipawn_evaluation, centipawn_diff))
        previous_evaluation = centipawn_evaluation

    return evaluations

def evaluate_chess_games(stockfish_path : str, 
                         depth : int, 
                         storage_directory : str, 
                         storage_test_directory : str, 
                         start_ply : int, 
                         end_ply : int):
    '''
    This function evaluates chess games using the Stockfish engine and saves the evaluations to a new directory.
    The function reads partitions of games from the given storage directory, evaluates the games using the Stockfish engine,
    and writes the evaluated partitions to a test directory. It includes both the centipawn evaluation and the
    absolute difference in centipawn evaluation compared to the previous move within the same game.

    Args:
        stockfish_path         : Path to the Stockfish binary.
        depth                  : Depth for Stockfish evaluation (e.g., 20 for 20-ply depth).
        storage_directory      : Directory containing original partitions of games.
        storage_test_directory : Directory to write revised partitions.
        start_ply              : Starting total_ply value to process.
        end_ply                : Ending total_ply value to process.
    '''

    os.makedirs(storage_test_directory, exist_ok = True)

    for total_ply in range(start_ply, end_ply + 1):

        print(f"Processing total_ply={total_ply}...")
        partition_path = Path(storage_directory, f"total_ply={total_ply}", "data.parquet")

        if not partition_path.exists():
            continue

        df = pd.read_parquet(partition_path)

        with ProcessPoolExecutor() as executor:
            tasks         = [executor.submit(evaluate_game, game_id, df[df['game_id'] == game_id]['pgn'].iloc[0], stockfish_path, depth) for game_id in df['game_id'].unique()]
            evaluations   = [task.result() for task in tasks]

        evaluations        = [item for sublist in evaluations for item in sublist]
        eval_df            = pd.DataFrame(evaluations, columns=['game_id', 'ply', 'centipawn_evaluation', 'centipawn_diff'])
        df                 = df.merge(eval_df, on=['game_id', 'ply'], how='left')
        new_partition_dir  = os.path.dirname(partition_path.as_posix().replace(storage_directory, storage_test_directory))
        os.makedirs(new_partition_dir, exist_ok = True)  # Create new directory if needed
        new_partition_path = os.path.join(new_partition_dir, "data.parquet")
        df.to_parquet(new_partition_path)

        num_rows_path      = Path(storage_directory, f"total_ply={total_ply}", "num_rows.txt")
        if num_rows_path.exists():
            new_num_rows_path = os.path.join(new_partition_dir, "num_rows.txt")
            copyfile(num_rows_path, new_num_rows_path)

    print("Processing completed!")

def main():

    stockfish_path        = "Engines/Stockfish"               # Path to Stockfish binary
    depth                 = 20                                # Depth for Stockfish evaluation (e.g., 20 for 20-ply depth)
    storage_directory     = "../Project Scotch/Games/Storage" # Directory containing original partitions
    storage_test_directory = "Games/Storage"                  # Directory to write revised partitions
    start_ply             = 0                                # Starting total_ply value to process
    end_ply               = 350                               # Ending total_ply value to process

    evaluate_chess_games(stockfish_path, depth, storage_directory, storage_test_directory, start_ply, end_ply)

if __name__ == "__main__":
    main()

# Since each position has the same centipawn values, run all the positions once and then join them back into the full dataset, and then put the partitions back in the right places