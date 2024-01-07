'''
Created on Dec 24, 2023

@author: wlauer
'''
import unittest
import pathlib

from irs990v2.index import Index

class Test(unittest.TestCase):

    TEST_DIR = pathlib.Path(__file__).parent
    TEST_FILE =TEST_DIR.joinpath("index.csv")
    TEST_FILE_2019 =TEST_DIR.joinpath("index_2019.csv")


    def testIndex(self):
        with open(self.TEST_FILE, 'r', newline='') as f:
            idx = Index(f)
            self.assertEqual(len(idx.records), 3, 'validating number of records')
            self.assertEqual(len(idx), 3, 'validating __len__')
            
            d = idx[0]
            self.assertEquals(d['RETURN_ID'], '14046790')
            self.assertEquals(d['RETURN_TYPE'], '990EZ')
            
            ii=0
            for _ in idx:
                ii += 1
            
            self.assertEquals(ii, 3)
            
    def testProcess(self):
        with open(self.TEST_FILE, 'r', encoding='utf-8-sig', newline='') as file:

            for filing in Index.process(file, self.TEST_DIR, ['990', 'BondIssue']):
                d = next(filing['990'])
                self.assertEqual(d['ein'], '042103545')
                self.assertEqual(d['name'], 'TRUSTEES OF BOSTON COLLEGE')
                self.assertEqual(d['returntype'], '990')
                self.assertEqual(d['taxyear'], '2015')
                self.assertEqual(d['contributions'], '210570096')
                self.assertIsNone(d['priorperiodadjustments'])

                ii = 0
                bonds = filing['BondIssue']
                for b in bonds:
                    ii+=1
                    self.assertIsNotNone(b)
                    self.assertEqual(b['ein'], '042103545')
                    self.assertEqual(b['name'], 'TRUSTEES OF BOSTON COLLEGE')
                    self.assertIn(b['cusip'], ['57583RPC3', '57583RL45', '57583R4M4', '57583UZQ4'])
                self.assertEqual(ii, 4)

    def testProcessZip(self):
        with open(self.TEST_FILE_2019, 'r', encoding='utf-8-sig', newline='') as file:
            for filing in Index.processZip(file, self.TEST_DIR, None, ['990', 'BondIssue']):
                d = next(filing['990'])
                self.assertEqual(d['ein'], '550307300')
                self.assertEqual(d['name'], 'WEST VIRGINIA TRUCKING ASSOCIATION INC')
                self.assertEqual(d['returntype'], '990')
                self.assertEqual(d['taxyear'], '2017')
                self.assertEqual(d['contributions'], '83118')
                self.assertIsNone(d['priorperiodadjustments'])

                bonds = filing['BondIssue']
                self.assertEqual(len(list(bonds)), 0)


    def testExpandFilingsDir(self):    
        dirs = Index._expandFilingsDir(self.TEST_DIR)
    
        self.assertEqual(len(dirs), 1)
        self.assertIn('2017', dirs)
        self.assertIn(self.TEST_DIR.joinpath('2017').joinpath('filings'), dirs['2017'])
        self.assertIn(self.TEST_DIR.joinpath('2017').joinpath('filings2'), dirs['2017'])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testIndex']
    unittest.main()