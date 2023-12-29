'''
Created on Dec 22, 2023

@author: wlauer
'''
import configparser
from functools import cache
import importlib.resources
import re
import os

class Mapping():
    '''
    Class for loading XML Path mappings for fields to be extracted from 990 files
    '''

    schema: str
    mappings: configparser.ConfigParser

    def __init__(self, schema: str):
        '''
        Constructor
        '''
        self.schema = schema[:schema.rindex('v')]
        self.mappings = self.load_mappings(self.schema)
        
    @property
    def ein(self) -> str:
        """EIN XPath mapping""" 
        return self.mappings.get('Common', 'EIN')

    @property
    def name(self) -> str:
        """Name XPath mapping"""
        return self.mappings.get('Common', 'Name')
    
    @property
    def return_type(self) -> str:
        """Return type xpath mapping"""
        return self.mappings.get('Common', 'ReturnType')
    
    @property
    def tax_year(self) -> str:
        """Tax Year xpath mapping"""
        return self.mappings.get('Common', 'TaxYear')
    
    @property
    def tax_period_start_date(self) -> str:
        """Tax Period Start Date xpath mapping"""
        return self.mappings.get('Common', 'TaxPeriodStartDate')
    
    @property
    def tax_period_end_date(self) -> str:
        """Tax Period End Date xpath mapping"""
        return self.mappings.get('Common', 'TaxPeriodEndDate')
    
    @property
    def fields(self) -> list[tuple[str, str]]:
        """Return list of the remaining interesting fields."""
        return self.mappings.items('990')
        
    @classmethod
    @cache
    def load_mappings(cls, schema: str) -> configparser.ConfigParser:
        """Load the matching set of XPath mappings for the specified schema."""
        with importlib.resources.open_text('irs990v2', f'{schema}.ini') as mapping_file:
            config_parser = configparser.ConfigParser()
        
            config_parser.read_file(mapping_file)
            return config_parser
    
    @classmethod
    def all_mappings(cls) -> set[str]:
        mappings = set()
        
        with importlib.resources.files('irs990v2') as files:
            for f in files.iterdir():
                if re.match('.+\.ini', f.name):
                    config = cls.load_mappings(os.path.splitext(f.name)[0])
                    for name, _ in config.items('990'):
                        mappings.add(name)
        return mappings