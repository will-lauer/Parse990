#!/usr/local/bin/python2.7
# encoding: utf-8
'''
irs990.parse -- parse 990 xml files

irs990.parse is a parser to read 990 xml files

It defines classes_and_methods

@author:     Will Lauer

@copyright:  2023 Will Lauer. All rights reserved.

@license:    All rights Reserved

@contact:    will@wlauer.net
@deffield    updated: Updated
'''

import sys
import os
import xml.etree.ElementTree as ET

from os.path import join

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import csv

__all__ = []
__version__ = 0.1
__date__ = '2023-12-19'
__updated__ = '2023-12-19'

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    

class Irs990Parser():
    common_fields = {
            'TaxPeriodEndDate':     ['ReturnHeader/TaxPeriodEndDt',
                                     'ReturnHeader/TaxPeriodEndDate'],
            'TaxPeriodBeginDt':     ['ReturnHeader/TaxPeriodBeginDt',
                                     'ReturnHeader/TaxPeriodBeginDate'],
            'TaxYr':                ['ReturnHeader/TaxYr',
                                     'ReturnHeader/TaxYear'],
            'EIN':                  ['ReturnHeader/Filer/EIN'],
            'Name':                 ['ReturnHeader/Filer/BusinessName/BusinessNameLine1Txt',
                                     'ReturnHeader/Filer/Name/BusinessNameLine1'],
            'ReturnTypeCd':         ['ReturnHeader/ReturnTypeCd',
                                     'ReturnHeader/ReturnType'],
        }
    
    fields = {
            'TotalEndOfYearAssets':                     ['ReturnData/IRS990/TotalAssetsEOYAmt',
                                                         'ReturnData/IRS990/TotalAssetsEOY'],
            'TotalBeginOfYearAssets':                   ['ReturnData/IRS990/TotalAssetsBOYAmt',
                                                         'ReturnData/IRS990/TotalAssetsBOY'],
            'Contributions':                            ['ReturnData/IRS990/TotalContributionsAmt',
                                                         'ReturnData/IRS990/TotalContributions'],
            'ProgramRevenue':                           ['ReturnData/IRS990/TotalProgramServiceRevenueAmt',
                                                         'ReturnData/IRS990/TotalProgramServiceRevenue'],
            'FundraisingExpense':                       ['ReturnData/IRS990/TotalFunctionalExpensesGrp/FundraisingAmt',
                                                         'ReturnData/IRS990/TotalFunctionalExpenses/Fundraising'],
            'TotalRevenue':                             ['ReturnData/IRS990/CYTotalRevenueAmt',
                                                         'ReturnData/IRS990/TotalRevenueCurrentYear'],
            'TotalExpenses':                            ['ReturnData/IRS990/CYTotalExpensesAmt',
                                                         'ReturnData/IRS990/TotalExpensesAmtCurrentYear'],
            'InvestmentIncome':                         ['ReturnData/IRS990/CYInvestmentIncomeAmt',
                                                         'ReturnData/IRS990/InvestmentIncomeCurrentYear'],
            'OtherRevenue':                             ['ReturnData/IRS990/CYOtherRevenueAmt',
                                                         'ReturnData/IRS990/InvestmentIncomeCurrentYear'],
            'ManagementAndGeneralExpenses':             ['ReturnData/IRS990/TotalFunctionalExpensesGrp/ManagementAndGeneralAmt',
                                                         'ReturnData/IRS990/TotalFunctionalExpenses/ManagementAndGeneral'],
            'GovermentGrants':                          ['ReturnData/IRS990/GovernmentGrantsAmt',
                                                         'ReturnData/IRS990/GovernmentGrants'],
            'DepreciationAndDepletion':                 ['ReturnData/IRS990/DepreciationDepletionGrp/TotalAmt',
                                                         'ReturnData/IRS990/DepreciationDepletion/Total'],
            
            # Balance Sheet
            'CashEOY':                                  ['ReturnData/IRS990/CashNonInterestBearingGrp/EOYAmt',
                                                         'ReturnData/IRS990/CashNonInterestBearing/EOY'],
            'SavingsAndRemporaryCashInvestmentsEOY':    ['ReturnData/IRS990/SavingsAndTempCashInvstGrp/EOYAmt',
                                                         'ReturnData/IRS990/SavingsAndTempCashInvestments/EOY'],
            'PledgesReceivableEOY':                     ['ReturnData/IRS990/PledgesAndGrantsReceivableGrp/EOYAmt',
                                                         'ReturnData/IRS990/PledgesAndGrantsReceivable/EOY'],
            'AccountsReceivableEOY':                    ['ReturnData/IRS990/AccountsReceivableGrp/EOYAmt',
                                                         'ReturnData/IRS990/AccountsReceivable/EOY'],
            'ReceivablesFromOfficersEtc':               ['ReturnData/IRS990/ReceivablesFromOfficersEtcGrp/EOYAmt',
                                                         'ReturnData/IRS990/ReceivablesFromOfficersEtc/EOY'],
            'RcvblFromDisqualifiedPrsn':                ['ReturnData/IRS990/RcvblFromDisqualifiedPrsnGrp/EOYAmt',
                                                         'ReturnData/IRS990/ReceivablesFromDisqualPersons/EOY'],
            'OthNotesLoansReceivableNetGrp':            ['ReturnData/IRS990/OthNotesLoansReceivableNetGrp/EOYAmt',
                                                         'ReturnData/IRS990/OtherNotesLoansReceivableNet/EOY'],
            'InventoriesForSaleOrUseEOY':               ['ReturnData/IRS990/InventoriesForSaleOrUseGrp/EOYAmt',
                                                         'ReturnData/IRS990/InventoriesForSaleOrUse/EOY'],
            'PrepaidExpensesEOY':                       ['ReturnData/IRS990/PrepaidExpensesDefrdChargesGrp/EOYAmt',
                                                         'ReturnData/IRS990/PrepaidExpensesDeferredCharges/EOY'],
            'GrossFixedAssets':                         ['ReturnData/IRS990/LandBldgEquipCostOrOtherBssAmt',
                                                         'ReturnData/IRS990/LandBuildingsEquipmentBasis'],
            'AccumulatedDepreciation':                  ['ReturnData/IRS990/LandBldgEquipAccumDeprecAmt',
                                                         'ReturnData/IRS990/LandBldgEquipmentAccumDeprec'],
            'LandBldgEquipBasisNet':                    ['ReturnData/IRS990/LandBldgEquipBasisNetGrp/EOYAmt',
                                                         'ReturnData/IRS990/LandBuildingsEquipmentBasisNet/EOY'],
            'InvestmentsPubTradedSec':                  ['ReturnData/IRS990/InvestmentsPubTradedSecGrp/EOYAmt',
                                                         'ReturnData/IRS990/InvestmentsPubTradedSecurities/EOY'],
            'InvestmentsOtherSecurities':               ['ReturnData/IRS990/InvestmentsOtherSecuritiesGrp/EOYAmt',
                                                         'ReturnData/IRS990/InvestmentsOtherSecurities/EOY'],
            'InvestmentsProgramRelated':                ['ReturnData/IRS990/InvestmentsProgramRelatedGrp/EOYAmt',
                                                         'ReturnData/IRS990/InvestmentsProgramRelated/EOY'],
            'IntangibleAssets':                         ['ReturnData/IRS990/IntangibleAssetsGrp/EOYAmt',
                                                         'ReturnData/IRS990/IntangibleAssets/EOY'],
            'OtherAssetsTotal':                         ['ReturnData/IRS990/OtherAssetsTotalGrp/EOYAmt',
                                                         'ReturnData/IRS990/OtherAssetsTotal/EOY'],
            'TotalAssets':                              ['ReturnData/IRS990/TotalAssetsGrp/EOYAmt',
                                                         'ReturnData/IRS990/TotalAssets/EOY'],
            'AccountsPayableAccrExpnss':                ['ReturnData/IRS990/AccountsPayableAccrExpnssGrp/EOYAmt',
                                                         'ReturnData/IRS990/AccountsPayableAccruedExpenses/EOY'],
            'GrantsPayable':                            ['ReturnData/IRS990/GrantsPayableGrp/EOYAmt',
                                                         'ReturnData/IRS990/GrantsPayable/EOY'],
            'DeferredRevenueEOY':                       ['ReturnData/IRS990/DeferredRevenueGrp/EOYAmt',
                                                         'ReturnData/IRS990/DeferredRevenue/EOY'],
            'TaxExemptBondLiabilitiesEOY':              ['ReturnData/IRS990/TaxExemptBondLiabilitiesGrp/EOYAmt',
                                                         'ReturnData/IRS990/TaxExemptBondLiabilities/EOY'],
            'EscrowAccountLiabilityGrp':                ['ReturnData/IRS990/EscrowAccountLiabilityGrp/EOYAmt',
                                                         'ReturnData/IRS990/EscrowAccountLiability/EOY'],
            'LoansFromOfficersDirectorsEmployees':      ['ReturnData/IRS990/LoansFromOfficersDirectorsGrp/EOYAmt',
                                                         'ReturnData/IRS990/LoansFromOfficersDirectors/EOY'],
            'MortgageAndNotesPayableEOY':               ['ReturnData/IRS990/MortgNotesPyblScrdInvstPropGrp/EOYAmt',
                                                         'ReturnData/IRS990/MortNotesPyblSecuredInvestProp/EOY'],
            'UnsecuredNotesPayableEOY':                 ['ReturnData/IRS990/UnsecuredNotesLoansPayableGrp/EOYAmt',
                                                         'ReturnData/IRS990/UnsecuredNotesLoansPayable/EOY'],
            'OtherLiabilities':                         ['ReturnData/IRS990/OtherLiabilitiesGrp/EOYAmt',
                                                         'ReturnData/IRS990/OtherLiabilities/EOY'],
            'TotalLiabilitiesEOY':                      ['ReturnData/IRS990/TotalLiabilitiesGrp/EOYAmt',
                                                         'ReturnData/IRS990/TotalLiabilities/EOY'],
            'OrganizationFollowsSFAS117Ind':            ['ReturnData/IRS990/OrganizationFollowsSFAS117Ind',
                                                         'ReturnData/IRS990/FollowSFAS117'],
            'UnrestrictedNetAssets':                    ['ReturnData/IRS990/UnrestrictedNetAssetsGrp/EOYAmt',
                                                         'ReturnData/IRS990/UnrestrictedNetAssets/EOY'],
            'TemporarilyRstrNetAssets':                 ['ReturnData/IRS990/TemporarilyRstrNetAssetsGrp/EOYAmt',
                                                         'ReturnData/IRS990/TemporarilyRestrictedNetAssets/EOY'],
            'PermanentlyRstrNetAssets':                 ['ReturnData/IRS990/PermanentlyRstrNetAssetsGrp/EOYAmt',
                                                         'ReturnData/IRS990/PermanentlyRestrictedNetAssets/EOY'],
            'CapStkTrPrinCurrentFunds':                 ['ReturnData/IRS990/CapStkTrPrinCurrentFundsGrp/EOYAmt',
                                                         'ReturnData/IRS990/CapStckTrstPrinCurrentFunds/EOY'],
            'PdInCapSrplsLandBldgEqpFund':              ['ReturnData/IRS990/PdInCapSrplsLandBldgEqpFundGrp/EOYAmt',
                                                         'ReturnData/IRS990/PaidInCapSrplsLandBldgEqpFund/EOY'],
            'RtnEarnEndowmentIncmOthFnds':              ['ReturnData/IRS990/RtnEarnEndowmentIncmOthFndsGrp/EOYAmt',
                                                         'ReturnData/IRS990/RetainedEarningsEndowmentEtc/EOY'],
            'TotalNetAssetsEOY':                        ['ReturnData/IRS990/TotalNetAssetsFundBalanceGrp/EOYAmt',
                                                         'ReturnData/IRS990/TotalNetAssetsFundBalances/EOY'],
            'TotLiabNetAssetsFundBalance':              ['ReturnData/IRS990/TotLiabNetAssetsFundBalanceGrp/EOYAmt',
                                                         'ReturnData/IRS990/TotalLiabNetAssetsFundBalances/EOY'],
            
            # Part XI Reconciliation of net assets
            'PriorPeriodAdjustments':                   ['ReturnData/IRS990/PriorPeriodAdjustmentsAmt',
                                                         'ReturnData/IRS990/ReconcilationPriorAdjustment'],
            'OtherChangesInNetAssets':                  ['ReturnData/IRS990/OtherChangesInNetAssetsAmt',
                                                         'ReturnData/IRS990/ReconcilationOtherChanges']
            
        }
    
    schedulek = 'b:ReturnData/b:IRS990ScheduleK'
    bond_issue = ['b:TaxExemptBondsIssuesGrp',
                  'b:Form990ScheduleKPartI'
        ]
    
    cusip_fields = {
            'CUSIP':            ['b:ReturnData/b:IRS990ScheduleK[{0}]/b:TaxExemptBondsIssuesGrp[{1}]/b:CUSIPNum',
                                 'b:ReturnData/b:IRS990ScheduleK[{0}]/b:Form990ScheduleKPartI[{1}]/b:CUSIPNumber'],
            'IssuerEIN':        ['b:ReturnData/b:IRS990ScheduleK[{0}]/b:TaxExemptBondsIssuesGrp[{1}]/b:BondIssuerEIN',
                                 'b:ReturnData/b:IRS990ScheduleK[{0}]/b:Form990ScheduleKPartI[{1}]/b:IssuerEIN'],
            'IssuerName':       ['b:ReturnData/b:IRS990ScheduleK[{0}]/b:TaxExemptBondsIssuesGrp[{1}]/b:IssuerName/b:BusinessNameLine1Txt',
                                 'b:ReturnData/b:IRS990ScheduleK[{0}]/b:Form990ScheduleKPartI[{1}]/b:IssuerName/b:BusinessNameLine1'],
            'BondIssuedDt':     ['b:ReturnData/b:IRS990ScheduleK[{0}]/b:TaxExemptBondsIssuesGrp[{1}]/b:BondIssuedDt',
                                 'b:ReturnData/b:IRS990ScheduleK[{0}]/b:Form990ScheduleKPartI[{1}]/b:DateIssued'],
            'IssuePriceAmt':    ['b:ReturnData/b:IRS990ScheduleK[{0}]/b:TaxExemptBondsIssuesGrp[{1}]/b:IssuePriceAmt',
                                 'b:ReturnData/b:IRS990ScheduleK[{0}]/b:Form990ScheduleKPartI[{1}]/b:IssuePrice']
        }
    
    
    
    def __init__(self):
        pass
    
    def walk(self, path, writer, cusipwriter):
        for dirpath, _, filenames in os.walk(path):
            print(dirpath)
            for filename in filenames:
                self.parse(join(dirpath, filename), writer, cusipwriter)
    
    def parse(self, path, writer, cusipwriter):
        row = dict()
        cusip_rows = list()

        try:
            root = ET.parse(path)
            
            for field in self.common_fields:
                row[field] = ''
                for val in self._findall(root, self.common_fields[field], {'':'http://www.irs.gov/efile'}):
                    row[field] = val.text
    
            for field in self.fields:
                row[field] = 0
                for val in self._findall(root, self.fields[field], {'':'http://www.irs.gov/efile'}):
                    row[field] = val.text
            
            schedks = self._findall(root, [self.schedulek], {'b':'http://www.irs.gov/efile'})
            
            kk = 0
            for _ in schedks:
                kk += 1
                bonds = self._findall(root, [self.schedulek + f'[{str(kk)}]/' + b for b in self.bond_issue], {'b':'http://www.irs.gov/efile'})
                
                ii = 0
                for _ in bonds:
                    cusip_row = dict()
                    
                    ii+=1
                    for field in self.common_fields:
                        cusip_row[field] = row[field]
                    for field in self.cusip_fields:
                        cusip_row[field] = ''
                        for val in self._findall(root, self.cusip_fields[field], {'b':'http://www.irs.gov/efile'}, kk, ii):
                            cusip_row[field] = val.text
                    
                    cusip_rows.append(cusip_row)
        except Exception as e:
            print(f"Error processing {path}:")
            print(repr(e))
        
        writer.writerow(row)
        cusipwriter.writerows(cusip_rows)

    def _findall(self, tree, fields, namespaces, *args):
        for field in fields:
            result = tree.findall(field.format(*args), namespaces)
            if len(result) > 0:
                return result
        return list()
          


def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Will Lauer on %s.
  Copyright 2023 Will Lauer. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-o', '--output', dest="output", help="output file", metavar='file')
        parser.add_argument('-c', '--cusip-output', dest='cusip_output', help="CUSIP output file", metavar='cusip out')
        parser.add_argument('-d', '--dir', dest="paths", action='extend', default=[], help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')
        parser.add_argument('-f', '--file', dest="files", action='extend', default=[], help="paths to source file", metavar="file", nargs="+")

        # Process arguments
        args = parser.parse_args()

        paths = args.paths
        files = args.files
        output = args.output or 'output.csv'
        cusip_output = args.cusip_output or 'output-cusip.csv'

        parser = Irs990Parser()
        
        with open(output, 'w', newline='') as csvfile, open(cusip_output, 'w', newline='') as cusipcsvfile:
            fieldnames = list(parser.common_fields.keys())
            fieldnames.extend(list(parser.fields.keys()))
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            cusipfieldnames = list(parser.common_fields.keys())
            cusipfieldnames.extend(list(parser.cusip_fields.keys()))
            cusipwriter = csv.DictWriter(cusipcsvfile, fieldnames = cusipfieldnames)
            
            cusipwriter.writeheader()

            for inpath in paths:
                ### do something with inpath ###
                #print(f"parser.walk('{inpath}')")
                parser.walk(inpath, writer, cusipwriter)
            
            for infile in files:
                #print(f"parser.parse('{infile}')")
                parser.parse(infile, writer, cusipwriter)
        
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())