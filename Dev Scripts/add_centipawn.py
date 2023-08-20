from concurrent.futures import ProcessPoolExecutor
from stockfish import Stockfish
import chess.pgn
import pandas as pd
import os
from pathlib import Path
from io import StringIO
import gc

def evaluate_game(args):
    game_id, pgn, stockfish_path, depth = args
    stockfish = Stockfish(path=stockfish_path, depth=depth)
    return _evaluate_game(game_id, pgn, stockfish)

def _evaluate_game(game_id: int, pgn: str, stockfish: Stockfish) -> list:
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    evaluations = []
    board = game.board()
    previous_evaluation = None

    for move in game.mainline_moves():
        board.push(move)
        stockfish.set_fen_position(board.fen())
        centipawn_evaluation = stockfish.get_evaluation()['value']
        centipawn_diff = abs(centipawn_evaluation - previous_evaluation) if previous_evaluation is not None else 0
        evaluations.append((game_id, board.ply(), centipawn_evaluation, centipawn_diff))
        previous_evaluation = centipawn_evaluation

    return evaluations

def evaluate_chess_games(stockfish_path: str, depth: int, storage_directory: str, storage_test_directory: str, start_ply: int, end_ply: int):
    os.makedirs(storage_test_directory, exist_ok=True)

    for total_ply in range(end_ply, start_ply - 1, -1):
        print(f"Processing total_ply={total_ply}...")
        partition_path = Path(storage_directory, f"total_ply={total_ply}", "data.parquet")
        if not partition_path.exists():
            continue

        df = pd.read_parquet(partition_path)
        evaluations = []

        with ProcessPoolExecutor() as executor:
            tasks = [executor.submit(evaluate_game, (game_id, pgn, stockfish_path, depth)) for game_id, pgn in df[['game_id', 'pgn']].itertuples(index=False)]
            for task in tasks:
                evaluations.extend(task.result())

        # Create a DataFrame with the evaluations
        eval_df = pd.DataFrame(evaluations, columns=['game_id', 'ply', 'centipawn_evaluation', 'centipawn_diff'])
        df = df.merge(eval_df, on=['game_id', 'ply'], how='left')
        new_partition_dir = Path(storage_test_directory, f"total_ply={total_ply}")
        os.makedirs(new_partition_dir, exist_ok=True)
        new_partition_path = os.path.join(new_partition_dir, "data.parquet")
        df.to_parquet(new_partition_path)

        # Explicitly trigger garbage collection
        gc.collect()

    print("Processing completed!")

def main():
    stockfish_path = "Engines/Stockfish"
    depth = 10 # Reduced depth
    storage_directory = "/Users/Macington/Documents/Projects/Project Scotch/Games/Storage"
    storage_test_directory = "/Users/Macington/Documents/Projects/Project Gambit/Games/Storage"
    start_ply = 47
    end_ply = 289

    evaluate_chess_games(stockfish_path, depth, storage_directory, storage_test_directory, start_ply, end_ply)

if __name__ == "__main__":
    main()