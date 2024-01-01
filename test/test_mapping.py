'''
Created on Dec 24, 2023

@author: wlauer
'''
import unittest

from irs990v2.mapping import Mapping

class Test(unittest.TestCase):


    def testMapping(self):
        m2013v20 = Mapping('2013v2.0')
        m2013v21 = Mapping('2013v2.1')
        m2016v30 = Mapping('2016v3.0')
        m2016v31 = Mapping('2016v3.1')
        m2017v22 = Mapping('2017v2.2')
    
        self.assertTrue(m2013v20.mappings is m2013v21.mappings, 'verify caching of 2013')
        self.assertTrue(m2016v30.mappings is m2016v31.mappings)
        self.assertFalse(m2016v31.mappings is m2017v22.mappings)
    
    def testMapping2013v2(self):
        m = Mapping('2013v2.0')
        
        self.assertEquals(m.ein, 'ReturnHeader/Filer/EIN')
        self.assertEquals(m.name, 'ReturnHeader/Filer/BusinessName/BusinessNameLine1')
        self.assertEquals(m.tax_year, 'ReturnHeader/TaxYr')
        
        f = m.fields('990')
        
        (name, val) = f[0]
        self.assertEquals(name, 'contributions')
        self.assertEquals(val, 'CYContributionsGrantsAmt')
        
        self.assertEquals(len(f), 51)
    
    def testMapping2016v3(self):
        m = Mapping('2016v3.0')
        
        self.assertEquals(m.ein, 'ReturnHeader/Filer/EIN')
        self.assertEquals(m.name, 'ReturnHeader/Filer/BusinessName/BusinessNameLine1Txt')
        self.assertEquals(m.tax_year, 'ReturnHeader/TaxYr')
        
        f = m.fields('990')
        
        (name, val) = f[0]
        self.assertEquals(name, 'contributions')
        self.assertEquals(val, 'CYContributionsGrantsAmt')
        
        self.assertEquals(len(f), 51)
    
    def testAllMappings(self):
        s = Mapping.all_mappings('990')
        
        self.assertEqual(len(s), 51)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testMapping']
    unittest.main()