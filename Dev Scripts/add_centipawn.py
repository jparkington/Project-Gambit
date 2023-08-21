from stockfish import Stockfish
import chess.pgn
import numpy as np
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
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

# Directory containing the Parquet files
parquet_dir = "/Users/Macington/Documents/Projects/Project Gambit/Games/Storage"

print("Reading all Parquet files in the directory...")
# Read all Parquet files in the directory
dataset = ds.dataset(parquet_dir, format="parquet")
table = dataset.to_table()
partitioning_scheme = dataset.partitioning

# Convert to Pandas DataFrame
df = table.to_pandas()

# Identify unique board_sum_in_context values where centipawn_evaluation is null
print("Identifying unique board_sum_in_context values where centipawn_evaluation is null...")
unique_board_sums = df[df['centipawn_evaluation'].isnull()]['board_sum_in_context'].unique()

print(f"Found {len(unique_board_sums)} unique board_sum_in_context values with missing centipawn_evaluation.")

# Stockfish configuration
stockfish_path = "Engines/Stockfish"
depth = 10

# Chunk size
chunk_size = 50

# Evaluate each unique board_sum_in_context with Stockfish in chunks
print("Evaluating missing centipawn_evaluation values using Stockfish...")
for chunk_start in np.arange(0, len(unique_board_sums), chunk_size):
    chunk_end = min(chunk_start + chunk_size, len(unique_board_sums))
    print(f"Processing chunk {chunk_start} to {chunk_end}...")
    for board_sum_in_context in unique_board_sums[chunk_start:chunk_end]:
        # Get the corresponding pgn
        pgn = df[df['board_sum_in_context'] == board_sum_in_context]['pgn'].iloc[0]
        # Evaluate the position
        centipawn_evaluation = evaluate_position(pgn, stockfish_path, depth)
        # Update the DataFrame safar
        df.loc[df['board_sum_in_context'] == board_sum_in_context, 'centipawn_evaluation'] = centipawn_evaluation

    print("Converting the updated DataFrame back to a pyarrow Table...")
    # Convert the updated DataFrame back to a pyarrow Table
    table = pa.Table.from_pandas(df)

    print("Writing the updated Table back to the Parquet directory...")
    # Write the updated Table back to the Parquet directory
    pq.write_to_dataset(table, root_path=parquet_dir, partitioning=partitioning_scheme)

    print(f"Chunk {chunk_start} to {chunk_end} processed!")

print("Missing centipawn_evaluation values have been filled based on board_sum_in_context. Process completed!")