from stockfish import Stockfish
import chess.pgn
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from io import StringIO

def evaluate_position(stockfish, pgn: str, depth: int) -> int:
    pgn_io = StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    stockfish.set_fen_position(board.fen())
    return stockfish.get_evaluation()['value']

# Directory containing the Parquet files
parquet_dir = "/Users/Macington/Documents/Projects/Project Gambit/Games/St"

# Read the Ply.parquet file
ply_file_path = f"{parquet_dir}/ply.parquet"
ply_table = pq.read_table(ply_file_path)
ply_df = ply_table.to_pandas()

# Read the PGNs.parquet file
pgns_file_path = f"{parquet_dir}/pgn.parquet"
pgns_table = pq.read_table(pgns_file_path)
pgns_df = pgns_table.to_pandas()

# Merge the pgn into ply based on 'pgn_id'
ply_df = ply_df.merge(pgns_df[['pgn_id', 'pgn']], on='pgn_id', how='inner')

# Identify all unique progression_hash values and their corresponding pgn
unique_progression_hashes = ply_df[['progression_hash', 'pgn']].drop_duplicates()

# Stockfish configuration
stockfish_path = "Engines/Stockfish"
depth = 10

# Initialize Stockfish instance
stockfish = Stockfish(path=stockfish_path, depth=depth)

# Chunk size
chunk_size = 5000

# Evaluate each unique progression_hash with Stockfish in chunks
for chunk_start in np.arange(0, len(unique_progression_hashes), chunk_size):
    chunk_end = min(chunk_start + chunk_size, len(unique_progression_hashes))
    print(f"Processing chunk {chunk_start} to {chunk_end}...")
    progression_hash_to_centipawn = {}
    for progression_hash in unique_progression_hashes[chunk_start:chunk_end]:
        if progression_hash == 6548726006382385350:
            centipawn = 0
        else:
            # Get the corresponding pgn
            pgn = ply_df[ply_df['progression_hash'] == progression_hash]['pgn'].iloc[0]
            # Evaluate the position
            centipawn = evaluate_position(pgn, stockfish_path, depth)
        progression_hash_to_centipawn[progression_hash] = centipawn

    # Update the DataFrame using NumPy for efficiency
    ply_df['centipawn'] = ply_df['progression_hash'].map(progression_hash_to_centipawn).fillna(ply_df['centipawn']).astype(np.float32)

    print("Converting the updated DataFrame back to a pyarrow Table...")
    # Convert the updated DataFrame back to a pyarrow Table
    ply_table = pa.Table.from_pandas(ply_df)

    print("Writing the updated Table back to the Parquet file...")
    # Write the updated Table back to the Parquet file
    pq.write_table(ply_table, ply_file_path)

    print(f"Chunk {chunk_start} to {chunk_end} processed!")

print("Centipawn values have been filled based on progression_hash. Process completed!")