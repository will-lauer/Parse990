'''
Created on Dec 28, 2023

@author: wlauer
'''

from argparse import ArgumentParser
import os
import csv
from irs990v2.mapping import Mapping
from irs990v2.index import Index

def main(args: list[str] = None):
    argparser = ArgumentParser(description='Parse 990 filings')
    argparser.add_argument('-d', '--directory', dest='directory', help='directory with 990 xml files')
    argparser.add_argument('-i', '--index', dest='index', help='index file listing 990''s to parse')
    argparser.add_argument('-o', '--output', dest='out',help='output directory')
    argparser.add_argument('-f', '--forms', dest='forms', default='990', choices=['990', 'BondIssue'],
                           help='forms to process (default = 990)', nargs='*')
    
    args = argparser.parse_args(args=args)
    
    with open(args.index, 'r', newline='') as index:
        output_files = {f: open(os.path.join(args.out, f + '.csv'), 'w', newline='') for f in args.forms}
        
        base_fieldnames = {'ein', 'name', 'returntype', 'taxyear', 'taxperiodstart', 'taxperiodend'}
        fieldnames = {f: base_fieldnames | Mapping.all_mappings(f) for f in args.forms}
        
        writer = {f: csv.DictWriter(output_files[f], fieldnames=fieldnames[f]) for f in args.forms}
        
        for f in args.forms:
            writer[f].writeheader()
        
        for filing in Index.process(index, args.directory, args.forms):
            for f in args.forms:
                writer[f].writerows(filing[f])
        
        for w in writer.values():
            w.close()

if __name__ == "__main__":
    main()