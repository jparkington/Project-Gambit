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

def evaluate_chess_games(stockfish_path: str, depth: int, storage_directory: str, start_ply: int, end_ply: int):
    # Create a dataset object
    dataset = ds.dataset(storage_directory, format="parquet")
    
    # Loop through fragments (partitions) in the dataset
    for fragment in dataset.get_fragments():
        # Extract total_ply value directly from the fragment path
        total_ply = int(fragment.path.split('/')[-2].split('=')[-1])

        # Check if the total_ply is within the specified range
        if start_ply <= total_ply <= end_ply:
            print(f"Processing fragment at {fragment.path}...")
            
            # Read a fragment into a Table
            table = fragment.to_table()
            # Convert to pandas DataFrame
            df = table.to_pandas()
            
            # Check if there are any NaN values in centipawn_evaluation
            if df['centipawn_evaluation'].isnull().sum() == 0:
                print("No NaN values found. Skipping...")
                continue
            
            evaluations_to_update = {}
            # Filter only the records with NaN centipawn_evaluation
            df_null_eval = df[df['centipawn_evaluation'].isnull()]
            with ProcessPoolExecutor() as executor:
                tasks = [executor.submit(evaluate_game, (game_id, pgn, stockfish_path, depth)) for game_id, pgn in df_null_eval[['game_id', 'pgn']].itertuples(index=False)]
                for task in tasks:
                    for game_id, ply, centipawn_evaluation, _ in task.result():
                        evaluations_to_update[df.loc[(df['game_id'] == game_id) & (df['ply'] == ply), 'board_sum_in_context'].iloc[0]] = centipawn_evaluation
            
            # Update centipawn_evaluation based on board_sum_in_context
            for board_sum_in_context, centipawn_evaluation in evaluations_to_update.items():
                df.loc[df['board_sum_in_context'] == board_sum_in_context, 'centipawn_evaluation'] = centipawn_evaluation
            
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
    start_ply = 47
    end_ply = 228

    evaluate_chess_games(stockfish_path, depth, storage_directory, start_ply, end_ply)

if __name__ == "__main__":
    main()

