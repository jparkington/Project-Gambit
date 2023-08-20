from stockfish import Stockfish
import chess.pgn
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

# Read all Parquet files in the directory
dataset = ds.dataset(parquet_dir, format="parquet")
table = dataset.to_table()

# Convert to Pandas DataFrame
df = table.to_pandas()

# Identify unique board_sum_in_context values where centipawn_evaluation is null
unique_board_sums = df[df['centipawn_evaluation'].isnull()]['board_sum_in_context'].unique()

# Stockfish configuration
stockfish_path = "Engines/Stockfish"
depth = 10

# Evaluate each unique board_sum_in_context with Stockfish
for board_sum_in_context in unique_board_sums:
    # Get the corresponding pgn
    pgn = df[df['board_sum_in_context'] == board_sum_in_context]['pgn'].iloc[0]
    # Evaluate the position
    centipawn_evaluation = evaluate_position(pgn, stockfish_path, depth)
    # Update the DataFrame
    df.loc[df['board_sum_in_context'] == board_sum_in_context, 'centipawn_evaluation'] = centipawn_evaluation

# Convert the updated DataFrame back to a pyarrow Table
table = pa.Table.from_pandas(df)

# Write the updated Table back to the Parquet directory
pq.write_to_dataset(table, root_path=parquet_dir, partition_cols=dataset.partition_names)

print("Missing centipawn_evaluation values have been filled based on board_sum_in_context.")
