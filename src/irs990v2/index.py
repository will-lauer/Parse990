'''
Created on Dec 22, 2023

@author: wlauer
'''
import typing
import csv
from collections.abc import Sequence

class Index(Sequence):
    '''
    Class for reading and accessing 990 index files
    '''
    
    records: list[dict[str, str]] = list()

    def __init__(self, csvdata: typing.TextIO, fieldnames: Sequence = None) -> None:
        '''
        Constructor
        '''
        reader = csv.DictReader(csvdata, fieldnames=fieldnames)
        #self.records = list()
        
        for record in reader:
            self.records.append(record)
    
    def __len__(self) -> int:
        return len(self.records)
    
    def __getitem__(self, key):
        return self.records[key]
        
    def __iter__(self) -> iter:
        return iter(self.records)
        