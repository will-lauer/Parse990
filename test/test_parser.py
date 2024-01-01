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
    

    def testParse(self):
        
        with open(self.TEST_FILE_2009, 'r', encoding='utf-8-sig', newline='') as file:
            p = Parser()
            r = p.parse(file, ['990'])
            row = next(r['990'])
            
            self.assertEqual(len(row), 57)
            self.assertEqual(row['ein'], '042103545')
            self.assertEqual(row['returntype'], '990')
            self.assertEqual(row['name'], 'TRUSTEES OF BOSTON COLLEGE')
            self.assertIsNone(row['priorperiodadjustments'])

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