'''
Created on Dec 25, 2023

@author: wlauer
'''
import unittest
import pathlib

from irs990v2.parse import Parser
from wsgiref.handlers import IISCGIHandler

class Test(unittest.TestCase):
    
    TEST_DIR = pathlib.Path(__file__).parent

    TEST_FILE_2009 = TEST_DIR.joinpath("0421035452009.txt")
    TEST_FILE_2019 = TEST_DIR.joinpath("0421035452019.txt")
    

    def testParse(self):
        
        with open(self.TEST_FILE_2009, 'r', encoding='utf-8-sig', newline='') as file:
            p = Parser()
            r = p.parse(file, ['990', 'BondIssue'])
            row = next(r['990'])
            
            self.assertEqual(len(row), 57)
            self.assertEqual(row['ein'], '042103545')
            self.assertEqual(row['returntype'], '990')
            self.assertEqual(row['name'], 'TRUSTEES OF BOSTON COLLEGE')
            self.assertIsNone(row['priorperiodadjustments'])
            
            ii = 0
            bonds = r['BondIssue']
            for b in bonds:
                ii+=1
                self.assertIsNotNone(b)
                self.assertEqual(b['ein'], '042103545')
                self.assertEqual(b['name'], 'TRUSTEES OF BOSTON COLLEGE')
                self.assertIn(b['cusip'], ['57585K6M5', '57583RPC3', '57583RL45'])
            
            self.assertEqual(ii, 3)

        with open(self.TEST_FILE_2019, 'r', encoding='utf-8-sig', newline='') as file:
            p = Parser()
            r = p.parse(file, ['990'])
            row = next(r['990'])
            
            self.assertEqual(len(row), 57)
            self.assertEqual(row['ein'], '042103545')
            self.assertEqual(row['returntype'], '990')
            self.assertEqual(row['name'], 'TRUSTEES OF BOSTON COLLEGE')
            self.assertIsNone(row['priorperiodadjustments'])
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()