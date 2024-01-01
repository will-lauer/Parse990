'''
Created on Dec 22, 2023

@author: wlauer
'''
import configparser
from functools import cache
import importlib.resources

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
    
    def fields(self, form: str = '990') -> list[tuple[str, str]]:
        """Return list of the remaining interesting fields."""
        return self.mappings.items(form)
    
    def base_path(self, form: str):
        """Return the base path mapping for the specified form."""
        return self.mappings.get('Common', form)
        
    @classmethod
    @cache
    def load_mappings(cls, schema: str) -> configparser.ConfigParser:
        """Load the matching set of XPath mappings for the specified schema."""
        with importlib.resources.open_text('irs990v2', f'{schema}.ini') as mapping_file:
            config_parser = configparser.ConfigParser()
        
            config_parser.read_file(mapping_file)
            return config_parser
    
    @classmethod
    def all_mappings(cls, form: str) -> set[str]:
        mappings = set()

        with importlib.resources.open_text('irs990v2', 'template.ini') as mapping_file:
            config = configparser.ConfigParser()
            config.read_file(mapping_file)
            for name, _ in config.items(form):
                mappings.add(name)

        return mappings