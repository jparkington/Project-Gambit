'''
Author:        James Parkington
Created Date:  5/8/2023
Modified Date: 7/9/2023

File containing the Utility class for data storage and retrieval.
'''

from   tkinter import filedialog
from   typing  import *
import os
import sys
import pandas          as pd
import pyarrow.parquet as pq

class Utility:
    '''
    The Utility class provides methods for data storage and retrieval. It allows for reading from and writing to 
    Parquet files, and provides convenience methods for managing Parquet datasets.

    Attributes:
        pq_name  (str) : The name of the Parquet dataset.
        pq_path  (str) : The path to the Parquet dataset.
        pgn_path (str) : The path to the PGN file.

    Methods:
        open_file    : Opens a file dialog and returns the selected file path as a string.
        from_parquet : Reads a set of partitions from the Parquet dataset and returns them as a DataFrame. 
        get_metadata : Retrieves the metadata for each partition in the Parquet dataset.
        __call__     : Returns the path to the PGN file, which is obtained either from the command line arguments or a file dialog.
    '''

    def __init__(self, pq_name: str = "Storage"):

        self.pq_name  = pq_name
        self.pq_path  = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'../Games/{self.pq_name}')
        self.pgn_path = None

    def open_file(self, file_type: str = 'PGN') -> str:
        '''
        Opens a file dialog and returns the selected file path as a string. The file type defaults to "PGN".

        Parameters:
            file_type: The type of file to open. Defaults to "PGN".

        Returns:
            The selected file path as a string.
        '''

        file_path = filedialog.askopenfilename(title = f'Select a {file_type} file', filetypes = [(f'{file_type} files', f'*.{file_type.lower()}')])

        if not file_path:
            return None

        return file_path

    def __call__(self) -> str:
        '''
        Returns the path to the PGN file. If the path has not been set yet, it attempts to obtain it either from the 
        command line arguments or a file dialog.

        Returns:
            The path to the PGN file as a string.
        '''

        if self.pgn_path is None:
            self.pgn_path = sys.argv[1] if len(sys.argv) > 1 else self.open_file()
        
        return self.pgn_path