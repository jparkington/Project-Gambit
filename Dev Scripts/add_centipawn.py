from concurrent.futures import ProcessPoolExecutor
from stockfish import Stockfish
import chess.pgn
import pandas as pd
import os
from pathlib import Path
from io import StringIO
import gc
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pyarrow as pa

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
    
def evaluate_chess_games(stockfish_path: str, depth: int, storage_directory: str):
    # Create a dataset object
    dataset = ds.dataset(storage_directory, format="parquet")

    # Loop through fragments (partitions) in the dataset
    for fragment in dataset.get_fragments():
        print(f"Processing fragment at {fragment.path}...")
        
        # Read a fragment into a Table
        table = fragment.to_table()
        # Convert to pandas DataFrame
        df = table.to_pandas()
        
        # Check if there are any NaN values in centipawn_evaluation
        if df['centipawn_evaluation'].isnull().sum() == 0:
            print("No NaN values found. Skipping...")
            continue
        
        evaluations = []
        # Filter only the records with NaN centipawn_evaluation
        df_null_eval = df[df['centipawn_evaluation'].isnull()]
        with ProcessPoolExecutor() as executor:
            tasks = [executor.submit(evaluate_game, (game_id, pgn, stockfish_path, depth)) for game_id, pgn in df_null_eval[['game_id', 'pgn']].itertuples(index=False)]
            for task in tasks:
                evaluations.extend(task.result())
        
        # Create a DataFrame with the evaluations
        eval_df = pd.DataFrame(evaluations, columns=['game_id', 'ply', 'centipawn_evaluation', 'centipawn_diff'])
        df.update(eval_df)
        
        # Convert back to pyarrow Table
        updated_table = pa.Table.from_pandas(df)
        
        # Write the updated Table back to the fragment's location
        pq.write_table(updated_table, fragment.path)

        # Explicitly trigger garbage collection
        gc.collect()

    print("Processing completed!")

def main():
    stockfish_path = "Engines/Stockfish"
    depth = 10 # Reduced depth
    storage_directory = "/Users/Macington/Documents/Projects/Project Gambit/Games/Storage"

    evaluate_chess_games(stockfish_path, depth, storage_directory)

if __name__ == "__main__":
    main()
