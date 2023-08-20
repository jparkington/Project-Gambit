from stockfish import Stockfish
import chess.pgn
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pyarrow as pa
from io import StringIO

def evaluate_position(pgn: str, stockfish_path: str, depth: int) -> int:
    stockfish = Stockfish(path=stockfish_path, depth=depth)
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    stockfish.set_fen_position(board.fen())
    return stockfish.get_evaluation()['value']

def evaluate_chess_games(stockfish_path: str, depth: int, storage_directory: str):
    # Create a dataset object
    dataset = ds.dataset(storage_directory, format="parquet")

    # Load the schema of the dataset
    original_schema = dataset.schema

    # Create a new schema by casting all integer fields to float64
    new_schema = pa.schema([(field.name, pa.float64() if pa.types.is_integer(field.type) else field.type) for field in original_schema])

    # Load the entire dataset into a Table with the new schema
    table = dataset.to_table(schema=new_schema)

    # Convert to pandas DataFrame
    df = table.to_pandas()

    # Filter records with null centipawn_evaluation
    null_eval_df = df[df['centipawn_evaluation'].isnull()]

    # Group by board_sum_in_context and sort by the count of null records
    unique_board_sums = null_eval_df.groupby('board_sum_in_context').size().reset_index(name='counts').sort_values('counts', ascending=False)

    # Evaluate each unique board_sum_in_context with Stockfish
    for board_sum_in_context in unique_board_sums['board_sum_in_context']:
        # Get the corresponding pgn
        pgn = null_eval_df[null_eval_df['board_sum_in_context'] == board_sum_in_context]['pgn'].iloc[0]
        # Evaluate the position
        centipawn_evaluation = evaluate_position(pgn, stockfish_path, depth)
        # Update the DataFrame
        df.loc[df['board_sum_in_context'] == board_sum_in_context, 'centipawn_evaluation'] = centipawn_evaluation

    # Convert back to pyarrow Table
    updated_table = pa.Table.from_pandas(df)

    # Write the updated Table back to the original location
    pq.write_to_dataset(updated_table, root_path=storage_directory, format="parquet")

    print("Processing completed!")m

def main():
    stockfish_path = "Engines/Stockfish"
    depth = 10 # Adjust as needed
    storage_directory = "/Users/Macington/Documents/Projects/Project Gambit/Games/Storage"

    evaluate_chess_games(stockfish_path, depth, storage_directory)

if __name__ == "__main__":
    main()