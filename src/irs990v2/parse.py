'''
Created on Dec 22, 2023

@author: wlauer
'''
import typing
import re
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from .index import Index
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
    
    def processIndex(self, index: typing.TextIO, filings_dir: str) -> typing.Generator[dict[str,str], None, None]:
        idx = Index(index)
        
        dirs = self._expandFilingsDir(filings_dir)
        
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
                            yield self.parse990(f)
                            break
        
    
    def parse990(self, filing: typing.TextIO) -> dict[str, str]:
        row = dict()
        
        try:
            root = ET.parse(filing)
            schema_version = root.getroot().get('returnVersion')
            
            mapping = Mapping(schema_version)
            
            row['ein'] = self._find(root, mapping.ein)
            row['name'] = self._find(root, mapping.name)
            row['returntype'] = self._find(root, mapping.return_type)
            row['taxyear'] = self._find(root, mapping.tax_year)
            row['taxperiodstart'] = self._find(root, mapping.tax_period_start_date)
            row['taxperiodend'] = self._find(root, mapping.tax_period_end_date)
                        
            # for name, xpath in mapping.fields:
            #     row[name] = self._find(root, xpath)
            for elem in root.iterfind('./ReturnData/IRS990', self.DEFAULT_NAMESPACE):
                print(elem)
                for name, field in mapping.fields:
                    f = elem.find(os.path.basename(field), self.DEFAULT_NAMESPACE)
                    print(f'{name}: {f}')
            
            return row
        except Exception as e:
            print(f'Error processing {filing.name}:')
            print(repr(e))
    
    def _find(self, tree: ET, field: str, namespaces: dict[str, str] = DEFAULT_NAMESPACE):
        if field != '':
            elem = tree.findall(field, namespaces)
            if len(elem) > 0:
                return elem[0].text
        return None
    
    def _expandFilingsDir(self, filings_dir:str) -> dict[str, list[Path]]:
        dirs = dict()
        for year_dir in os.scandir(filings_dir):
            if year_dir.is_dir() and re.match('[0-9]{4}', year_dir.name):
                for subdir in os.scandir(year_dir.path):
                    if subdir.is_dir():
                        dirs.setdefault(year_dir.name, list()).append(Path(subdir.path))
        
        return dirs
