'''
Created on Dec 28, 2023

@author: wlauer
'''

from argparse import ArgumentParser
import csv
from irs990v2.parse import Parser
from irs990v2.mapping import Mapping

if __name__ == "__main__":
    argparser = ArgumentParser(description='Parse 990 filings')
    argparser.add_argument('-d', '--directory', dest='directory', help='directory with 990 xml files')
    argparser.add_argument('-i', '--index', dest='index', help='index file listing 990''s to parse')
    argparser.add_argument('-o', '--output', dest='out',help='output file')
    
    args = argparser.parse_args()
    
    parser = Parser()
    
    with open(args.out, 'w', newline='') as csvfile, open(args.index, 'r', newline='') as index:
        fieldnames = ['ein', 'name', 'returntype', 'taxyear', 'taxperiodstart', 'taxperiodend']
        fieldnames.extend(Mapping.all_mappings())
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        writer.writerows(parser.processIndex(index, args.directory))