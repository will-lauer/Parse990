'''
Created on Dec 25, 2023

@author: wlauer
'''
import unittest
import pathlib

from irs990v2.parse import Parser

class Test(unittest.TestCase):
    
    TEST_DIR = pathlib.Path(__file__).parent

    TEST_FILE_2009 = TEST_DIR.joinpath("0421035452009.txt")
    TEST_FILE_2019 = TEST_DIR.joinpath("0421035452019.txt")
    
    TEST_INDEX = pathlib.Path(__file__).parent.joinpath("index.csv")

    def testParse990(self):
        
        with open(self.TEST_FILE_2009, 'r', encoding='utf-8-sig', newline='') as file:
            p = Parser()
            row = p.parse990(file)
            
            self.assertEqual(len(row), 57)
            self.assertEqual(row['ein'], '042103545')
            self.assertEqual(row['returntype'], '990')
            self.assertEqual(row['name'], 'TRUSTEES OF BOSTON COLLEGE')
            self.assertIsNone(row['priorperiodadjustments'])

        with open(self.TEST_FILE_2019, 'r', encoding='utf-8-sig', newline='') as file:
            p = Parser()
            row = p.parse990(file)
            
            self.assertEqual(len(row), 57)
            self.assertEqual(row['ein'], '042103545')
            self.assertEqual(row['returntype'], '990')
            self.assertEqual(row['name'], 'TRUSTEES OF BOSTON COLLEGE')
            self.assertIsNone(row['priorperiodadjustments'])
        
    def testIndex(self):
        with open(self.TEST_INDEX, 'r', encoding='utf-8-sig', newline='') as file:
            p = Parser()
            for d in p.processIndex(file, self.TEST_DIR):
                print(d)
                self.assertEqual(d['ein'], '042103545')
                self.assertEqual(d['name'], 'TRUSTEES OF BOSTON COLLEGE')
                self.assertEqual(d['returntype'], '990')
                self.assertEqual(d['taxyear'], '2015')
                self.assertEqual(d['contributions'], '210570096')
                self.assertIsNone(d['priorperiodadjustments'])
    
    def testExpandFilingsDir(self):
        p = Parser()
        
        dirs = p._expandFilingsDir(self.TEST_DIR)
        
        self.assertEqual(len(dirs), 1)
        self.assertIn('2017', dirs)
        self.assertIn(self.TEST_DIR.joinpath('2017').joinpath('filings'), dirs['2017'])
        self.assertIn(self.TEST_DIR.joinpath('2017').joinpath('filings2'), dirs['2017'])
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()