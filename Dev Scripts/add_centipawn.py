from stockfish import Stockfish
import chess.pgn
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from io import StringIO

print("Starting script...")

def evaluate_position(board, stockfish_path, depth):
    stockfish = Stockfish(path=stockfish_path, depth=depth)
    stockfish.set_fen_position(board.fen())
    return stockfish.get_evaluation()['value']

print("Reading Parquet files...")
# File paths
ply_file_path = "/Users/Macington/Documents/Projects/Project Gambit/Games/ply.parquet"
pgns_file_path = "/Users/Macington/Documents/Projects/Project Gambit/Games/pgn.parquet"

# Read the Ply.parquet file
ply_table = pq.read_table(ply_file_path)
ply_df = ply_table.to_pandas()

# Add 'centipawn' column if not already present
if 'centipawn' not in ply_df.columns:
    ply_df['centipawn'] = np.nan

# Read the PGNs.parquet file
pgns_table = pq.read_table(pgns_file_path)
pgns_df = pgns_table.to_pandas()

# Merge the pgn into ply based on 'pgn_id'
ply_df = ply_df.merge(pgns_df[['pgn_id', 'pgn']], on='pgn_id', how='inner')

print("Configuring Stockfish...")
# Stockfish configuration
stockfish_path = "Engines/Stockfish"
depth = 10

# Chunk size
chunk_size = 1000

print("Processing rows where centipawn is null...")
# Process rows where centipawn is null
remaining_rows_df = ply_df[ply_df['centipawn'].isnull()]

# Process unique pgn values for remaining rows
unique_pgns = remaining_rows_df['pgn_id'].unique()
progression_hash_centipawn = {}  # To store centipawn values based on progression_hash
for pgn_index, pgn_id in enumerate(unique_pgns):
    print(f"Processing pgn_id {pgn_id} ({pgn_index + 1}/{len(unique_pgns)})...")
    pgn_rows = ply_df[ply_df['pgn_id'] == pgn_id]
    pgn_text = pgn_rows['pgn'].iloc[0]

    # Read the PGN string and set up the game board
    pgn_io = StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()

    # Iterate through the moves in the pgn
    for ply, move in enumerate(game.mainline_moves()):
        board.push(move)
        progression_hash = pgn_rows[pgn_rows['ply'] == ply]['progression_hash'].iloc[0]

        # Evaluate the centipawn value only if it's null and not evaluated before
        if progression_hash not in progression_hash_centipawn:
            centipawn = evaluate_position(board, stockfish_path, depth)
            progression_hash_centipawn[progression_hash] = centipawn

            # Copy down the centipawn value to all matching progression_hash values
            ply_df.loc[ply_df['progression_hash'] == progression_hash, 'centipawn'] = centipawn

    # Write updated chunk back to Parquet file if needed
    if pgn_index % chunk_size == 0 and pgn_index > 0:
        ply_table = pa.Table.from_pandas(ply_df)
        pq.write_table(ply_table, ply_file_path)
        print(f"Chunk up to {pgn_index} processed!")

# Write final updated Parquet file
ply_table = pa.Table.from_pandas(ply_df)
pq.write_table(ply_table, ply_file_path)
print("Processing completed!")