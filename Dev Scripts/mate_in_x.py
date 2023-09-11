from typing import *
import pandas as pd
import numpy as np

def correct_mate_in_x_notation(df: pd.DataFrame) -> pd.DataFrame:
    '''
    This function corrects and updates the "centipawn" column in a DataFrame containing chess game notations. The process is as follows:

        1. Max Ply Calculation        : Determines the maximum ply (move count) for each game (denoted by 'pgn_id').
        2. Ply Distance From End      : Calculates how far each move is from the end of its respective game.
        3. Centipawn Difference       : Computes the difference between consecutive 'centipawn' values within each game.
        4. Standard Deviation         : Calculates a running average and standard deviation of the 'centipawn' difference within each game.
        5. Dynamic Significance Level : Sets a dynamic threshold for significance based on two times the running standard deviation.
        6. Significant Deviation      : Marks moves with 'centipawn' values that significantly deviate from the running average.
        7. Incorrect Notation Filter  : Identifies entries that need correction based on all the defined conditions above.
        8. Centipawn Value Correction : Updates the 'centipawn' value for incorrect entries with a large constant (e.g., 10^5) factored by the sign and a correction term.
        9. Checkmate Correction       : Updates NaN 'centipawn' values at ply_from_end = 0 to -10^5 as these are assumed to be checkmate conditions.

    Arguments:
        df: DataFrame containing the chess game notations with 'pgn_id', 'ply', and 'centipawn' columns.

    Returns:
        df: DataFrame with corrected 'centipawn' column.
    '''

    # Step 1 & 2
    df['max_ply']      = df.groupby('pgn_id')['ply'].transform('max')
    df['ply_from_end'] = df['max_ply'] - df['ply']
    
    # Step 3 & 4
    df['centipawn_diff'] = df.groupby('pgn_id')['centipawn'].diff().fillna(0)
    window_size          = 10
    df['running_avg']    = df.groupby('pgn_id')['centipawn_diff'].transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
    df['running_std']    = df.groupby('pgn_id')['centipawn_diff'].transform(lambda x: x.rolling(window=window_size, min_periods=1).std().fillna(0))
    
    # Step 5 & 6
    dynamic_significance_level  = df['running_std'] * 2
    df['significant_deviation'] = np.abs(df['centipawn_diff'] - df['running_avg']) >= dynamic_significance_level
    
    # Step 7
    df['interval_condition'] = (df['centipawn'].between(-50, 50)) & (df['centipawn'] != 0)
    df['near_end_condition'] = np.abs(np.abs(df['centipawn']) - df['ply_from_end']) <= 5
    df['ply_not_zero']       = df['ply'] != 0
    df['incorrect_notation'] = df['significant_deviation'] & df['interval_condition'] & df['near_end_condition'] & df['ply_not_zero']

    df['prev_incorrect_notation']   = df.groupby('pgn_id')['incorrect_notation'].shift(1).fillna(False)
    df['subsequent_mate_condition'] = df['prev_incorrect_notation'] & df['centipawn_diff'].isin([1, -1])
    df['incorrect_notation']        = df['incorrect_notation'] | df['subsequent_mate_condition']

    # Step 8 & 9
    large_constant = 10 ** 5

    non_nan_condition = df['incorrect_notation']
    df.loc[non_nan_condition, 'centipawn'] = np.sign(df.loc[non_nan_condition, 'centipawn']) * large_constant + -1 * df.loc[non_nan_condition, 'centipawn']
    
    nan_condition = (df['ply_from_end'] == 0) & (df['ply'] != 0) & df['centipawn'].isna()
    df.loc[nan_condition, 'centipawn'] = -large_constant

    return df