'''
Created on Dec 24, 2023

@author: wlauer
'''
import unittest
import pathlib

from irs990v2.index import Index

class Test(unittest.TestCase):

    TEST_FILE = pathlib.Path(__file__).parent.joinpath("index.csv")

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

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testIndex']
    unittest.main()