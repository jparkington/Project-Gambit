import os
import pandas as pd
from   pathlib import Path

def count_unique_game_ids_and_total_rows(storage_directory: str) -> (int, int):
    '''
    This function counts the number of unique game IDs and total rows across all partitions in the specified storage directory.
    
    It loops through all total_ply directories, checks if the data.parquet file exists, and then reads the Parquet file. 
    It adds unique game IDs from this partition to the set and the number of rows in this partition to the total.

    Arguments:
        storage_directory : Directory containing the partitions.

    Returns:
        total_unique_game_ids : The total count of unique game IDs.
        total_rows            : The total number of rows.
    '''

    unique_game_ids = set()
    total_rows      = 0
    storage_path    = Path(storage_directory)

    for total_ply_dir in storage_path.iterdir():

        if total_ply_dir.is_dir():
            partition_path = total_ply_dir / "data.parquet"

            if partition_path.exists():
                df = pd.read_parquet(partition_path)
                unique_game_ids.update(df['game_id'].unique())
                total_rows += len(df)

    total_unique_game_ids = len(unique_game_ids)

    print(f"Total number of unique game IDs : {total_unique_game_ids}")
    print(f"Total number of rows            : {total_rows}")

    return total_unique_game_ids, total_rows

def main():
    
    # Get the current script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the storage directory relative to the script's location
    storage_directory = os.path.join(script_directory, "../Games/Storage")

    count_unique_game_ids_and_total_rows(storage_directory)

if __name__ == "__main__":
    main()
