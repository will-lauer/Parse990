'''
Created on Dec 22, 2023

@author: wlauer
'''
import typing
import csv
import re
import os
from pathlib import Path
from collections.abc import Sequence
from typing import Generator

from .parse import Parser

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
    
    @classmethod
    def process(cls, index: typing.TextIO, filings_dir: str, forms: list[str] = ['990']) -> Generator[dict[str, Generator[dict[str, str], None, None]], None, None]:
        idx = Index(index)
        parser = Parser()

        dirs = cls._expandFilingsDir(filings_dir)
        
        for filing in idx:
            if filing['RETURN_TYPE'] == '990':
                objectid = filing['OBJECT_ID']
                year = objectid[:4]

                if year not in dirs:
                    continue
                for d in dirs[year]:
                    file = d.joinpath(f'{objectid}_public.xml')
                    if file.is_file():
                        with open(file, 'r', newline='', encoding='utf-8-sig') as f:
                            yield parser.parse(f, forms)
                            break
    @classmethod
    def _expandFilingsDir(cls, filings_dir:str) -> dict[str, list[Path]]:
        dirs = dict()
        for year_dir in os.scandir(filings_dir):
            if year_dir.is_dir() and re.match('[0-9]{4}', year_dir.name):
                for subdir in os.scandir(year_dir.path):
                    if subdir.is_dir():
                        dirs.setdefault(year_dir.name, list()).append(Path(subdir.path))
        
        return dirs
