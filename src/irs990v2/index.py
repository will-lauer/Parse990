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
from zipfile import ZipFile
import zipfile_deflate64

from .parse import Parser

class Index(Sequence):
    '''
    Class for reading and accessing 990 index files
    '''
    
    records: list[dict[str, str]]

    def __init__(self, csvdata: typing.TextIO, fieldnames: Sequence = None) -> None:
        '''
        Constructor
        '''
        reader = csv.DictReader(csvdata, fieldnames=fieldnames)
        
        self.records = list()
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
            # Ignore 990EZ, 990EO (alias for 990EZ), and 990PF filings.
            # Accept only 990 and 990O (alias for 990)
            if filing['RETURN_TYPE'] == '990' or filing['RETURN_TYPE'] == '990O':
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
    def processZip(cls, 
                   index: typing.TextIO, 
                   index_dir: typing.Union[str, bytes, os.PathLike], 
                   prior_index_dir: typing.Union[str, bytes, os.PathLike],
                   forms: list[str] = ['990']) -> Generator[dict[str, Generator[dict[str, str], None, None]], None, None]:
        
        idx = Index(index)
        parser = Parser()

        zip_files = list()
        zip_entries = dict()

        for file in os.scandir(index_dir):
            if file.is_file() and re.match('.*\.zip', file.name):
                archive = ZipFile(file.path)
                zip_files.append(archive)
                for name in archive.namelist():
                    zip_entries.setdefault(name, archive)
        
        if prior_index_dir is not None:
            for file in os.scandir(prior_index_dir):
                if file.is_file() and re.match('.*\.zip', file.name):
                    archive = ZipFile(file.path)
                    zip_files.append(archive)
                    for name in archive.namelist():
                        zip_entries.setdefault(name, archive)

        for filing in idx:
            # Ignore 990EZ, 990EO (alias for 990EZ), and 990PF filings.
            # Accept only 990 and 990O (alias for 990)
            if filing['RETURN_TYPE'] == '990' or filing['RETURN_TYPE'] == '990O':
                objectid = filing['OBJECT_ID']
                file = f'{objectid}_public.xml'
                archive = zip_entries[file]
                with archive.open(file, mode='r') as f:
                    yield parser.parse(f, forms)
                    break

        for archive in zip_files:
            archive.close()
    
    @classmethod
    def _expandFilingsDir(cls, filings_dir:str) -> dict[str, list[Path]]:
        dirs = dict()
        for year_dir in os.scandir(filings_dir):
            if year_dir.is_dir() and re.match('[0-9]{4}', year_dir.name):
                for subdir in os.scandir(year_dir.path):
                    if subdir.is_dir():
                        dirs.setdefault(year_dir.name, list()).append(Path(subdir.path))
        
        return dirs
