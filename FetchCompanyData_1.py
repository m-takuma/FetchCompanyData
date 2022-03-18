import datetime
from enum import Enum
import glob
from html import unescape
import os
import time
from arelle import Cntlr
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from FetchCompanyData import FetchXBRLFileClass, ParseXBRLFileClass
from bs4 import BeautifulSoup

cred = credentials.Certificate('C://Users//taku3//Dropbox//Biz//FetchCompanyData//corporateanalysishubapp-firebase-adminsdk-n8sd4-07e702dbc7.json')
db = None



class OptionFinData:
    class ElementName(Enum):
        #duration
        eps_jp = "BasicEarningsLossPerShareSummaryOfBusinessResults"
        eps_us = "BasicEarningsLossPerShareUSGAAPSummaryOfBusinessResults"
        eps_ifrs = "BasicEarningsLossPerShareIFRSSummaryOfBusinessResults"

        #instant
        bps_jp = "NetAssetsPerShareSummaryOfBusinessResults"
        bps_us = "EquityAttributableToOwnersOfParentPerShareUSGAAPSummaryOfBusinessResults"
        bps_ifrs = "EquityToAssetRatioIFRSSummaryOfBusinessResults"

        #duration
        dividend = "DividendPaidPerShareSummaryOfBusinessResults"


    eps = None
    bps = None
    dividend = None

    def parse(self,fact,accountStandard,isConsolidated) -> bool:
        if accountStandard == "IFRS":
            return self.parse_ifrs(fact)
        elif accountStandard == "US GAAP":
            return self.parse_usgaap(fact)
        elif accountStandard == "Japan GAAP":
            return self.parse_jpgaap(fact,isConsolidated)
        else:
            print("Error: 会計基準が判別できませんでした")
            return False

    def parse_ifrs(self,fact) -> bool:
        name = fact.concept.name
        contextID = fact.contextID
        element = self.ElementName
        if name == element.eps_ifrs.value and contextID == "CurrentYearDuration":
            self.eps = fact.value
        elif name == element.bps_ifrs.value and contextID == "CurrentYearInstant":
            self.bps = fact.value
        elif name == element.dividend.value and contextID == "CurrentYearDuration_NonConsolidatedMember":
            self.dividend = fact.value
        else:
            return False
        return True

    def parse_usgaap(self,fact) -> bool:
        name = fact.concept.name
        contextID = fact.contextID
        element = self.ElementName
        if name == element.eps_us.value and contextID == "CurrentYearDuration":
            self.eps = fact.value
        elif name == element.bps_us.value and contextID == "CurrentYearInstant":
            self.bps = fact.value
        elif name == element.dividend.value and contextID == "CurrentYearDuration_NonConsolidatedMember":
            self.dividend = fact.value
        else:
            return False
        return True

    def parse_jpgaap(self,fact,isConsolidated) -> bool:
        name = fact.concept.name
        contextID = fact.contextID
        element = self.ElementName
        if isConsolidated == "true":
            if name == element.eps_jp.value and contextID == "CurrentYearDuration":
                self.eps = fact.value
            elif name == element.bps_jp.value and contextID == "CurrentYearInstant":
                self.bps = fact.value
            elif name == element.dividend.value and contextID == "CurrentYearDuration_NonConsolidatedMember":
                self.dividend = fact.value
            else:
                return False
        elif isConsolidated == "false":
            if name == element.eps_jp.value and contextID == "CurrentYearDuration_NonConsolidatedMember":
                self.eps = fact.value
            elif name == element.bps_jp.value and contextID == "CurrentYearInstant_NonConsolidatedMember":
                self.bps = fact.value
            elif name == element.dividend.value and contextID == "CurrentYearDuration_NonConsolidatedMember":
                self.dividend = fact.value
            else:
                return False
        
        return True
            
        

class FS_HTML_Data:
    class ElementName(Enum):
        bs_html_JP_consolidated = "ConsolidatedBalanceSheetTextBlock"
        bs_html_JP_Nonconsolidated = "BalanceSheetTextBlock"
        bs_html_USGAAP_consolidated = "ConsolidatedBalanceSheetUSGAAPTextBlock"
        bs_html_IFRS_consolidated = "ConsolidatedStatementOfFinancialPositionIFRSTextBlock"

        pl_html_JP_consolidated = "ConsolidatedStatementOfIncomeTextBlock"
        pl_html_JP_Nonconsolidated = "StatementOfIncomeTextBlock"
        pl_html_USGAAP_consolidated = "ConsolidatedStatementOfIncomeUSGAAPTextBlock"
        pl_html_IFRS_consolidated = "ConsolidatedStatementOfProfitOrLossIFRSTextBlock"

        cf_html_JP_consolidated = "ConsolidatedStatementOfCashFlowsTextBlock"
        cf_html_JP_Nonconsolidated = "StatementOfCashFlowsTextBlock"
        cf_html_USGAAP_consolidated = "ConsolidatedStatementOfCashFlowsUSGAAPTextBlock"
        cf_html_IFRS_consolidated = "ConsolidatedStatementOfCashFlowsIFRSTextBlock"
    
    bs_html = None
    pl_html = None
    cf_html = None

    def parse(self,fact,accountStandard,isConsolidated) -> bool:
        if accountStandard == "IFRS":
            return self.parse_ifrs(fact)
        elif accountStandard == "US GAAP":
            return self.parse_usgaap(fact)
        elif accountStandard == "Japan GAAP":
            return self.parse_jpgaap(fact,isConsolidated)
        else:
            print("Error: 会計基準が判別できませんでした")
            return False

    def parse_ifrs(self,fact) -> bool:
        name = fact.concept.name
        element = self.ElementName
        if name == element.bs_html_IFRS_consolidated.value:
            self.bs_html = html_encode(fact.value)
        elif name == element.pl_html_IFRS_consolidated.value:
            self.pl_html = html_encode(fact.value)
        elif name == element.cf_html_IFRS_consolidated.value:
            self.cf_html = html_encode(fact.value)
        else:
            return False
        return True

    def parse_usgaap(self,fact) -> bool:
        name = fact.concept.name
        element = self.ElementName
        if name == element.bs_html_USGAAP_consolidated.value:
            self.bs_html = html_encode(fact.value)
        elif name == element.pl_html_USGAAP_consolidated.value:
            self.pl_html = html_encode(fact.value)
        elif name == element.cf_html_USGAAP_consolidated.value:
            self.cf_html = html_encode(fact.value)
        else:
            return False

        return True

    def parse_jpgaap(self,fact,isConsolidated):
        name = fact.concept.name
        element = self.ElementName
        if isConsolidated == "true":
            if name == element.bs_html_JP_consolidated.value:
                self.bs_html = html_encode(fact.value)
            elif name == element.pl_html_JP_consolidated.value:
                self.pl_html = html_encode(fact.value)
            elif name == element.cf_html_JP_consolidated.value:
                self.cf_html = html_encode(fact.value)
            else:
                return False
        else:
            if name == element.bs_html_JP_Nonconsolidated.value:
                self.bs_html = html_encode(fact.value)
            elif name == element.pl_html_JP_Nonconsolidated.value:
                self.pl_html = html_encode(fact.value)
            elif name == element.cf_html_JP_Nonconsolidated.value:
                self.cf_html = html_encode(fact.value)
            else:
                return False
        return True



class Company_HTML_Data:
    class ElementName(Enum):
        history = "CompanyHistoryTextBlock"
        descriptionOfBusiness = "DescriptionOfBusinessTextBlock"
        overviewOfAffiliatedEntities = "OverviewOfAffiliatedEntitiesTextBlock"
        infoAboutEmployees = "InformationAboutEmployeesTextBlock"
        bizPolicy = "BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock"
        bizRisks = "BusinessRisksTextBlock"
        analysis = "ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock"
        researchAndDevelopmentActivities = "ResearchAndDevelopmentActivitiesTextBlock"
        overviewOfCapitalExpenditures = "OverviewOfCapitalExpendituresEtcTextBlock"
        dividendPolicy = "DividendPolicyTextBlock"



    history = None
    descriptionOfBusiness = None
    overviewOfAffiliatedEntities = None
    infoAboutEmployees = None
    bizPolicy = None
    bizRisks = None
    analysis = None
    researchAndDevelopmentActivities = None
    overviewOfCapitalExpenditures = None
    dividendPolicy = None

    def parse(self,fact) -> bool:
        name = fact.concept.name
        element = self.ElementName
        if name == element.history.value:
            self.history = html_tprocessing(unescape(str(fact.value)))
        elif name == element.descriptionOfBusiness.value:
            self.descriptionOfBusiness = html_tprocessing(unescape(str(fact.value)))
        elif name == element.overviewOfAffiliatedEntities.value:
            self.overviewOfAffiliatedEntities = html_tprocessing(unescape(str(fact.value)))
        elif name == element.infoAboutEmployees.value:
            self.infoAboutEmployees = html_tprocessing(unescape(str(fact.value)))
        elif name == element.bizPolicy.value:
            self.bizPolicy = html_tprocessing(unescape(str(fact.value)))
        elif name == element.bizRisks.value:
            self.bizRisks = html_tprocessing(unescape(str(fact.value)))
        elif name == element.analysis.value:
            self.analysis = html_tprocessing(unescape(str(fact.value)))
        elif name == element.researchAndDevelopmentActivities.value:
            self.researchAndDevelopmentActivities = html_tprocessing(unescape(str(fact.value)))
        elif name == element.overviewOfCapitalExpenditures.value:
            self.overviewOfCapitalExpenditures = html_tprocessing(unescape(str(fact.value)))
        elif name == element.dividendPolicy.value:
            self.dividendPolicy = html_tprocessing(unescape(str(fact.value)))
        else:
            return False
        return True

def mainParse(facts,name):
    accounting_standard = None
    isConsolidated = None
    for fact in facts:
        if accounting_standard != None and isConsolidated != None:
            break
        elif fact.concept.name == "WhetherConsolidatedFinancialStatementsArePreparedDEI":
            isConsolidated = fact.value
        elif fact.concept.name == "AccountingStandardsDEI":
            accounting_standard = fact.value
        else:
            pass
    option_fin_data = OptionFinData()
    fs_html_data = FS_HTML_Data()
    company_html_data = Company_HTML_Data()
    for fact in facts:
        if option_fin_data.parse(fact,accounting_standard,isConsolidated) == True:
            pass
        elif company_html_data.parse(fact) == True: 
            pass
        else:
            fs_html_data.parse(fact,accounting_standard,isConsolidated)
    
    doc_ref = db.collection(u'TEST_TEST').document(name)
    doc_ref.set(option_fin_data.__dict__,merge=True)

    
    doc_ref.set(company_html_data.__dict__,merge=True)
    doc_ref.set(fs_html_data.__dict__,merge=True)


def html_encode(html:str) -> str:
    soup = BeautifulSoup(html)

    return(str(soup))

    

if __name__ == "__main__":
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    start = time.time()
    fetch_xbrl_file = FetchXBRLFileClass()
    parse_xbrl_file = ParseXBRLFileClass()

    ## ここでmodeを切り替える
    ### 0 : 内部データから取得
    ### 1 : APIを利用して特定の期間のデータをダウンロードして取得
    mode = 0
    ##
    
    folder_name_list = []

    if mode == 0:
        path = "D:D_Download//"
        files = os.listdir(path)
        dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
        folder_name_list = dir
    elif mode == 1:
        folder_name_list = fetch_xbrl_file.fetchXbrlFile(datetime.date(2022,1,1),datetime.date(2022,3,1))

    xbrl_files_path_parent = "D:D_Download//"
    xbrl_files_path_child = "//XBRL//PublicDoc//*.xbrl"

    for i in range(len(folder_name_list)):
        folder_name = folder_name_list[i]
        xbrl_files_path = glob.glob(f'{xbrl_files_path_parent}{folder_name}{xbrl_files_path_child}')
        fainalIndex = len(folder_name_list) - 1
        for j in range(len(xbrl_files_path)):
            file = xbrl_files_path[j]
            cntrl = Cntlr.Cntlr(logFileName='logToPrint')
            model_xbrl = cntrl.modelManager.load(file)
            mainParse(model_xbrl.facts,folder_name)
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
