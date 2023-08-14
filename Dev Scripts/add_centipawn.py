from concurrent.futures import ProcessPoolExecutor
from stockfish          import Stockfish
from pathlib            import Path
from io                 import StringIO
from typing             import List, Tuple
import chess.pgn
import pandas as pd
import os
import gc

def evaluate_game(game_id        : int, 
                  pgn            : str, 
                  stockfish_path : str, 
                  depth          : int) -> List[Tuple[int, int, int, int]]:
    '''
    Evaluate a single chess game using the Stockfish engine.

    This function evaluates the given chess game by iterating through its moves and using the Stockfish chess engine to 
    determine the centipawn evaluation at each move. The centipawn evaluation represents the advantage or disadvantage 
    in terms of hundredths of a pawn. A positive value indicates an advantage for White, while a negative value indicates 
    an advantage for Black.

    The function returns a list of evaluations, including the game ID, the ply (move number), the centipawn evaluation 
    at that move, and the absolute difference in centipawn evaluation compared to the previous move.

    Arguments:
        game_id         : Game ID to evaluate.
        pgn             : PGN (Portable Game Notation) string of the game.
        stockfish_path  : Path to Stockfish binary.
        depth           : Search depth for Stockfish, representing how many plies (half-moves) Stockfish will analyze 
                          before returning an evaluation.

    Returns:
        A list of evaluations for each move in the game, including:
            - game_id              : The game ID.
            - ply                  : The move number (ply) in the game.
            - centipawn_evaluation : The evaluation in centipawns at that move.
            - centipawn_diff       : The absolute difference in centipawns compared to the previous move.
    '''

    stockfish           = Stockfish(path = stockfish_path, depth = depth)
    pgn_io              = StringIO(pgn)
    game                = chess.pgn.read_game(pgn_io)
    evaluations         = []
    board               = game.board()
    previous_evaluation = None

    for move in game.mainline_moves():
        board.push(move)
        stockfish.set_fen_position(board.fen())
        centipawn_evaluation = stockfish.get_evaluation()['value']
        centipawn_diff       = abs(centipawn_evaluation - previous_evaluation) if previous_evaluation is not None else 0
        evaluations.append((game_id, board.ply(), centipawn_evaluation, centipawn_diff))
        previous_evaluation  = centipawn_evaluation

    return evaluations


def evaluate_chess_games(stockfish_path         : str, 
                         depth                  : int, 
                         storage_directory      : str, 
                         storage_test_directory : str, 
                         start_ply              : int, 
                         end_ply                : int):
    '''
    Evaluate a range of chess games using the Stockfish engine.

    Arguments:
        stockfish_path        : Path to Stockfish binary.
        depth                 : Search depth for Stockfish.
        storage_directory     : Directory containing original partitions.
        storage_test_directory: Directory to write revised partitions.
        start_ply             : Starting total_ply value to process.
        end_ply               : Ending total_ply value to process.
    '''
    os.makedirs(storage_test_directory, exist_ok = True)

    for total_ply in range(start_ply, end_ply + 1):
        print(f"Processing total_ply={total_ply}...")
        partition_path = Path(storage_directory, f"total_ply={total_ply}", "data.parquet")
        if not partition_path.exists():
            continue

        df          = pd.read_parquet(partition_path)
        evaluations = []

        with ProcessPoolExecutor() as executor:
            tasks = [executor.submit(evaluate_game, game_id, pgn, stockfish_path, depth) for game_id, pgn in df[['game_id', 'pgn']].itertuples(index=False)]
            for task in tasks:
                evaluations.extend(task.result())

        # Create DataFrame with evaluations
        eval_df            = pd.DataFrame(evaluations, columns=['game_id', 'ply', 'centipawn_evaluation', 'centipawn_diff'])
        df                 = df.merge(eval_df, on=['game_id', 'ply'], how='left')
        new_partition_dir  = Path(storage_test_directory, f"total_ply={total_ply}")
        os.makedirs(new_partition_dir, exist_ok = True)
        new_partition_path = os.path.join(new_partition_dir, "data.parquet")
        df.to_parquet(new_partition_path)

        # Explicitly trigger garbage collection
        gc.collect()

    print("Processing completed!")

def main():
    stockfish_path         = "Engines/Stockfish"
    depth                  = 10 # Reduced depth
    storage_directory      = "../Project Scotch/Games/Storage"
    storage_test_directory = "Games/Storage"
    start_ply              = 42
    end_ply                = 350

    evaluate_chess_games(stockfish_path, depth, storage_directory, storage_test_directory, start_ply, end_ply)

if __name__ == "__main__":
    main()
