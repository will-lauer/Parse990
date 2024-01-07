'''
Created on Dec 28, 2023

@author: wlauer
'''

from argparse import ArgumentParser
import os
import re
import csv
from zipfile import ZipFile
import zipfile_deflate64

from irs990v2.mapping import Mapping
from irs990v2.parse import Parser

def main(args: list[str] = None):
    argparser = ArgumentParser(description='Parse 990 filing zip files')
    argparser.add_argument('-d', '--directory', dest='directory', help='directory with 990 zip files')
    argparser.add_argument('-p', '--prefix', dest='prefix', help='output filename prefix')
    argparser.add_argument('-f', '--forms', dest='forms', default='990', choices=['990', 'BondIssue'],
                           help='forms to process (default = 990)', nargs='*')
    
    args = argparser.parse_args(args=args)
    
    output_files = {f: open(os.path.join(args.directory, f'{args.prefix}-{f}.csv'), 'w', newline='') for f in args.forms}
    
    base_fieldnames = ['ein', 'name', 'returntype', 'taxyear', 'taxperiodstart', 'taxperiodend']
    fieldnames = {f: base_fieldnames + list(Mapping.all_mappings(f)) for f in args.forms}
    
    writer = {f: csv.DictWriter(output_files[f], fieldnames=fieldnames[f]) for f in args.forms}

    for f in args.forms:
        writer[f].writeheader()
    
    parser = Parser()
    
    for file in os.scandir(args.directory):
        if file.is_file() and re.match('.*\.zip', file.name):
            with ZipFile(file.path) as archive:
                for name in archive.namelist():
                    filing = parser.parse(archive.open(name, mode='r'), args.forms)
                    for f in args.forms:
                        writer[f].writerows(filing[f])
   
    for w in output_files.values():
        w.close()        

if __name__ == "__main__":
    main()