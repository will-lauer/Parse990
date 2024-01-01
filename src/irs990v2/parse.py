'''
Created on Dec 22, 2023

@author: wlauer
'''
import typing
import xml.etree.ElementTree as ET
from typing import Generator

# from .index import Index
from .mapping import Mapping

class Parser(object):
    '''
    Parser to extract data from IRS 990 forms
    '''
    DEFAULT_NAMESPACE = {'':'http://www.irs.gov/efile'}


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def parse(self, filing: typing.TextIO, forms: list[str]) -> dict[str, Generator[dict[str, str], None, None]]:
        """ Parse 990 filing and return generator that produces a dictionary keyed by form with a value of a generator """
        base_row = dict()
        
        try:
            root = ET.parse(filing)
            schema_version = root.getroot().get('returnVersion')
            
            mapping = Mapping(schema_version)
            base_row['ein'] = self._find(root, mapping.ein)
            base_row['name'] = self._find(root, mapping.name)
            base_row['returntype'] = self._find(root, mapping.return_type)
            base_row['taxyear'] = self._find(root, mapping.tax_year)
            base_row['taxperiodstart'] = self._find(root, mapping.tax_period_start_date)
            base_row['taxperiodend'] = self._find(root, mapping.tax_period_end_date)
            
            row = dict()
            
            for form in forms:
                base_path = mapping.base_path(form)
                fields = mapping.fields(form)
                row[form] = self._details(root, base_path, fields, base_row)
            
            return row

        except Exception as e:
            print(f'Error processing {filing.name}:')
            print(repr(e))
        
        
    def _details(self, root: ET, base_path: str, fields: list[tuple[str, str]], base_row: dict[str, str]) -> Generator[dict[str, str], None, None]:
        """Return dictionary of generators with details from form"""
        for f in root.iterfind(base_path, self.DEFAULT_NAMESPACE):
            form_row = dict()
            form_row |= base_row
            
            for name, field in fields:
                form_row[name] = self._find(f, field)
            yield form_row

    
    def _find(self, tree: ET, field: str, namespaces: dict[str, str] = DEFAULT_NAMESPACE):
        if field != '':
            elem = tree.findall(field, namespaces)
            if len(elem) > 0:
                return elem[0].text
        return None
    