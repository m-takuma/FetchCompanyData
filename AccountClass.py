import datetime
from enum import Enum, auto
from html import unescape
from sys import flags
from tkinter.messagebox import NO
from typing import Any
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import jaconv
from numpy import double

# 列挙型

class IndustryCode(Enum):
    CTE = auto()
    """一般商工業"""
    BNK = auto()
    """銀行・信託業"""
    SEC = auto()
    """第一種金融商品取引業"""
    INS = auto()
    """保険業"""
    @classmethod
    def to_list(self) -> list:
        """列挙型の要素をリスト化する"""
        return (self._member_names_)

class AccountingStandardClass(Enum):
    japan_gaap = "Japan GAAP"
    ifrs = "IFRS"
    us_gaap = "US GAAP"
    @classmethod
    def to_list(self) -> list:
        """列挙型の要素をリスト化する"""
        return (self._member_names_)

# カスタムクラス

class CoreData:
    class CoreData(Enum):
        #EDINETコード
        EDINETCodeDEI = auto()
        #会計基準[Japan GAAP,US GAAP,IFRS,nil]
        AccountingStandardsDEI = auto()
        #証券コード
        SecurityCodeDEI = auto()
        #提出者名（日本語）
        FilerNameInJapaneseDEI = auto()
        #提出者名（英語）
        FilerNameInEnglishDEI = auto()
        #連結決算有無[true,false,nil]
        WhetherConsolidatedFinancialStatementsArePreparedDEI = auto()
        #別記事業（連結）
        IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = auto()
        #別記事業（個別）
        IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = auto()
        #当事業年度開始日
        CurrentFiscalYearStartDateDEI = auto()
        #当会計期間終了日
        CurrentPeriodEndDateDEI = auto()
        #当会計期間の種類[YT,HY,Q1,Q2,Q3,Q4,Q5]
        TypeOfCurrentPeriodDEI = auto()
        #当事業年度終了日
        CurrentFiscalYearEndDateDEI = auto()
        #事業年度名
        FiscalYearCoverPage = auto()
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    #EDINETコード
    EDINETCodeDEI = None
    #会計基準[Japan GAAP,US GAAP,IFRS,nil]
    AccountingStandardsDEI = None
    #証券コード
    SecurityCodeDEI = None
    #提出者名（日本語）
    FilerNameInJapaneseDEI = None
    #提出者名（英語）
    FilerNameInEnglishDEI = None
    #連結決算有無[true,false,nil]
    WhetherConsolidatedFinancialStatementsArePreparedDEI = None
    #別記事業（連結）
    IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = None
    #別記事業（個別）
    IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = None
    #当事業年度開始日
    CurrentFiscalYearStartDateDEI = None
    #当会計期間終了日
    CurrentPeriodEndDateDEI = None
    #当会計期間の種類[YT,HY,Q1,Q2,Q3,Q4,Q5]
    TypeOfCurrentPeriodDEI = None
    #当事業年度終了日
    CurrentFiscalYearEndDateDEI = None
    #事業年度名
    FiscalYearCoverPage = None
    simpleCompanyNameInJP = None
    """「株式会社」の除去、全角統一などの処理を施した会社名"""
    JCN = None
    """法人番号"""
    
    def __init__(self) -> None:
        self.EDINETCodeDEI = None
        self.AccountingStandardsDEI = None
        self.SecurityCodeDEI = None
        self.FilerNameInJapaneseDEI = None
        self.FilerNameInEnglishDEI = None
        self.WhetherConsolidatedFinancialStatementsArePreparedDEI = None
        self.IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = None
        self.IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = None
        self.CurrentFiscalYearStartDateDEI = None
        self.CurrentPeriodEndDateDEI = None
        self.TypeOfCurrentPeriodDEI = None
        self.CurrentFiscalYearEndDateDEI = None
        self.FiscalYearCoverPage = None
        self.simpleCompanyNameInJP = None
        self.JCN = None
        
    def main_parse(self,facts:list,jcn_dict:dict,sec_dict:dict):
        counter = 0
        for fact in facts:
            if self.p_parse(fact=fact) == True:
                counter = counter + 1
                if counter == len(self.CoreData.to_list()):break
        self.p_create_simpleCompanyNameInJP()
        self.p_check_secCode_whether_None(secCode_other=sec_dict.get(self.EDINETCodeDEI))
        self.JCN = jcn_dict.get(self.EDINETCodeDEI)       
    
    def p_check_secCode_whether_None(self,secCode_other):
        if self.SecurityCodeDEI == None:
            self.SecurityCodeDEI = secCode_other

    def p_parse(self,fact) -> bool:
        e = self.CoreData
        name = fact.concept.name
        if fact.value == "":
            return False
        elif name == e.EDINETCodeDEI.name:
            self.EDINETCodeDEI = fact.value
        elif name == e.AccountingStandardsDEI.name:
            self.AccountingStandardsDEI = fact.value
        elif name == e.SecurityCodeDEI.name:
            self.SecurityCodeDEI = str(fact.value)[:-1]
        elif name == e.FilerNameInJapaneseDEI.name:
            self.FilerNameInJapaneseDEI = fact.value
        elif name == e.FilerNameInEnglishDEI.name:
            self.FilerNameInEnglishDEI = fact.value
        elif name == e.WhetherConsolidatedFinancialStatementsArePreparedDEI.name:
            self.WhetherConsolidatedFinancialStatementsArePreparedDEI = fact.value
        elif name == e.IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI.name:
            self.IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = str(fact.value).upper()
        elif name == e.IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI.name:
            self.IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI = str(fact.value).upper()
        elif name == e.CurrentFiscalYearStartDateDEI.name:
            self.CurrentFiscalYearStartDateDEI = self.p_enc_from_str_to_date(fact.value)
        elif name == e.CurrentPeriodEndDateDEI.name:
            self.CurrentPeriodEndDateDEI = self.p_enc_from_str_to_date(fact.value)
        elif name == e.TypeOfCurrentPeriodDEI.name:
            self.TypeOfCurrentPeriodDEI = fact.value
        elif name == e.CurrentFiscalYearEndDateDEI.name:
            self.CurrentFiscalYearEndDateDEI = self.p_enc_from_str_to_date(fact.value)
        elif name == e.FiscalYearCoverPage.name:
            self.FiscalYearCoverPage = fact.value
        else:
            return False
        return True

    def p_enc_from_str_to_date(self,date_str) -> datetime.datetime:
        tdatetime = datetime.datetime.strptime(date_str,'%Y-%m-%d')
        tdate = datetime.datetime(tdatetime.year,tdatetime.month,tdatetime.day)
        return tdate
    
    def p_create_simpleCompanyNameInJP(self):
        self.simpleCompanyNameInJP = str(self.FilerNameInJapaneseDEI).replace(" ","")#半角スペースなくす
        self.simpleCompanyNameInJP = self.simpleCompanyNameInJP.replace("　","")#全角スペースなくす
        self.simpleCompanyNameInJP = self.simpleCompanyNameInJP.replace("株式会社","")#「株式会社」なくす
        self.simpleCompanyNameInJP = jaconv.h2z(text=self.simpleCompanyNameInJP,ascii=True,digit=True)

class DetailData:
    bs = None
    pl = None
    cf = None
    other = None
    fs_html = None
    company_html = None

    def __init__(self) -> None:
        self.bs = BS()
        self.pl = PL()
        self.cf = CF()
        self.other = OtherData()
        self.fs_html = FS_HTML_Data()
        self.company_html = Company_HTML_Data()
    
    def parse(self,facts:Any,coreData:CoreData):
        for fact in facts:
            if self.bs.main_parse(fact=fact,account_standard=coreData.AccountingStandardsDEI,isConsolidated=coreData.WhetherConsolidatedFinancialStatementsArePreparedDEI):pass
            elif self.pl.main_parse(fact=fact,account_standard=coreData.AccountingStandardsDEI,isConsolidated=coreData.WhetherConsolidatedFinancialStatementsArePreparedDEI):pass
            elif self.cf.main_parse(fact=fact,account_standard=coreData.AccountingStandardsDEI,isConsolidated=coreData.WhetherConsolidatedFinancialStatementsArePreparedDEI):pass
            elif self.other.main_parse(fact=fact):pass
            #elif self.fs_html.main_parse(fact=fact,account_standard=coreData.AccountingStandardsDEI,isConsolidated=coreData.WhetherConsolidatedFinancialStatementsArePreparedDEI):pass
            #elif self.company_html.main_parse(fact=fact):pass
            else:pass
        self.did_finish_parse(core=coreData)
        self.add_option_data(coreData=coreData)
    def did_finish_parse(self,core:CoreData):
        self.bs.did_finish_parse(core=core)

    def add_option_data(self,coreData:CoreData):
        if coreData.AccountingStandardsDEI == AccountingStandardClass.ifrs.value:
            self.pl.cal_operaitigIncome_from_ifrs()

class BS:

    def __init__(self) -> None:  
        self.assets = None
        """資産"""
        self.currentAssets = None
        """流動資産"""
        self.notesAndAccountsReceivableTrade = None
        """受取手形及び売掛金"""
        self.inventories = None
        """棚卸資産"""
        self.noncurrentAssets = None
        """非流動資産、固定資産"""
        self.propertyPlantAndEquipment = None
        """有形固定資産"""
        self.deferredAssets = None
        """繰延資産"""
        self.goodwill = None
        """のれん"""
        self.liabilities = None
        """負債"""
        self.interestBearingDebt = None
        """有利子負債"""
        self.currentLiabilities = None
        """流動負債"""
        self.notesAndAccountsPayableTrade = None
        """支払手形及び買掛金"""
        self.noncurrentLiabilities = None
        """非流動負債、固定負債"""
        self.netAssets = None
        """純資産"""
        self.shareholdersEquity = None
        """株主持分、自己資本"""
        self.retainedEarnings = None
        """利益剰余金"""
        self.treasuryStock = None
        """自己株式"""
        self.valuationAndTranslationAdjustments = None
        """その他包括利益累計額"""
        self.nonControllingInterests = None
        """非支配株主持分"""
        self.BPS = None
        """一株当たり純資産"""
    
    def did_finish_parse(self,core:CoreData):
        if core.AccountingStandardsDEI != AccountingStandardClass.japan_gaap.value:
            return
        
        contractAssets = 0
        contractLiabilities = 0
        notesAndAccountsReceivableTrade_temp = 0
        notesAndAccountsPayableTrade_temp = 0
        inventories_temp = 0

        if len(self.notesAndAccountsReceivableTrade) == 0:
            self.notesAndAccountsReceivableTrade = None
        else:
            if dict(self.notesAndAccountsReceivableTrade).get(self.JP.ContractAssets.name) != None:
                contractAssets = dict(self.notesAndAccountsReceivableTrade).get(self.JP.ContractAssets.name)
            if dict(self.notesAndAccountsReceivableTrade).get(self.JP.NotesAndAccountsReceivableTradeAndContractAssets.name) != None:
                notesAndAccountsReceivableTrade_temp = self.notesAndAccountsReceivableTrade[self.JP.NotesAndAccountsReceivableTradeAndContractAssets.name]
            else:
                for value in self.notesAndAccountsReceivableTrade.values():
                    notesAndAccountsReceivableTrade_temp += value

        if len(self.notesAndAccountsPayableTrade) == 0:
            self.notesAndAccountsPayableTrade = None
        else:
            if dict(self.notesAndAccountsPayableTrade).get(self.JP.ContractLiabilities.name) != None:
                contractLiabilities = dict(self.notesAndAccountsPayableTrade).get(self.JP.ContractLiabilities.name)
            for value in self.notesAndAccountsPayableTrade.values():
                notesAndAccountsPayableTrade_temp += value
        
        if len(self.inventories) == 0:
            self.inventories = None
        else:
            if dict(self.inventories).get(self.JP.Inventories.name) != None:
                inventories_temp = dict(self.inventories).get(self.JP.Inventories.name)
            else:
                for value in self.inventories.values():
                    inventories_temp += value
        
        self.notesAndAccountsReceivableTrade = notesAndAccountsReceivableTrade_temp - contractLiabilities
        self.notesAndAccountsPayableTrade = notesAndAccountsPayableTrade_temp - contractAssets
        self.inventories = inventories_temp


    
    def main_parse(self,fact,account_standard:str,isConsolidated:str) -> bool:
        if fact.value == "":
            return False
        if account_standard == AccountingStandardClass.ifrs.value:
            return self.p_ifrs_parse(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.us_gaap.value:
            return self.p_us_parse(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.japan_gaap.value:
            return self.p_jp_parse(fact=fact,isConsolidated=isConsolidated)
        else:
            return False
    
    def add_value_to_interestBearingDebt(self,value:int):
        if self.interestBearingDebt != None:
            self.interestBearingDebt = self.interestBearingDebt + value
        else:
            self.interestBearingDebt = value
    
    def p_jp_parse(self,fact,isConsolidated) -> bool:
        e = self.JP
        contextId = "CurrentYearInstant"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId = "CurrentYearInstant_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId:
            return False
        
        debt_list = [
            e.ShortTermBondsPayable.name,
            e.ShortTermLoansPayable.name,
            e.CommercialPapersLiabilities.name,
            e.CurrentPortionOfBonds.name,
            e.CurrentPortionOfLongTermLoansPayable.name,
            e.CurrentPortionOfConvertibleBonds.name,
            e.CurrentPortionOfBondsWithSubscriptionRightsToShares.name,
            e.BondsPayable.name,
            e.ConvertibleBonds.name,
            e.ConvertibleBondTypeBondsWithSubscriptionRightsToShares.name,
            e.BondsWithSubscriptionRightsToSharesNCL.name,
            e.LongTermLoansPayable.name
            ]

        notesAndAccountsReceivableTrade_ls = [
            e.NotesAndAccountsReceivableTradeAndContractAssets.name,
            e.NotesAndAccountsReceivableTrade.name,
            e.NotesReceivableTrade.name,
            e.AccountsReceivableTrade.name,
            e.ContractAssets.name,
            e.AccountsReceivableInstallment.name,
            e.ElectronicallyRecordedMonetaryClaimsOperatingCA.name,
            e.NotesReceivableAccountsReceivableFromCompletedConstructionContractsAndOtherCNS.name,
            e.NotesReceivableAccountsReceivableFromCompletedConstructionContractsCNS.name,
            e.AccountsReceivableFromCompletedConstructionContractsCNS.name
            ]

        notesAndAccountsPayableTrade_ls = [
            e.NotesAndAccountsPayableTrade.name,
            e.NotesPayableTrade.name,
            e.AccountsPayableTrade.name,
            e.ElectronicallyRecordedObligationsOperatingCL.name,
            e.NotesPayableAccountsPayableForConstructionContractsAndOtherCNS.name,
            e.NotesPayableAccountsPayableForConstructionContractsCNS.name,
            e.AccountsPayableForConstructionContractsCNS.name,
            e.ContractLiabilities.name
        ]

        inventories_ls = [
            e.Inventories.name,
            e.Merchandise.name,
            e.FinishedGoods.name,
            e.MerchandiseAndFinishedGoods.name,
            e.SemiFinishedGoods.name,
            e.RawMaterials.name,
            e.RawMaterialsAndSupplies.name,
            e.WorkInProcess.name,
            e.Supplies.name
        ]

        if self.notesAndAccountsReceivableTrade == None and self.notesAndAccountsPayableTrade == None and self.inventories == None:
            self.notesAndAccountsReceivableTrade = {}
            self.notesAndAccountsPayableTrade = {}
            self.inventories = {}
        
        if name == e.Assets.name:
            self.assets = int(fact.value)
        elif name == e.CurrentAssets.name:
            self.currentAssets = int(fact.value)
        elif name in notesAndAccountsReceivableTrade_ls:
            self.notesAndAccountsReceivableTrade[name] = int(fact.value)
        elif name in inventories_ls:
            self.inventories[name] = int(fact.value)
        elif name == e.NoncurrentAssets.name:
            self.noncurrentAssets = int(fact.value)
        elif name == e.PropertyPlantAndEquipment.name:
            self.propertyPlantAndEquipment = int(fact.value)
        elif name == e.DeferredAssets.name:
            self.deferredAssets = int(fact.value)
        elif name == e.Goodwill.name:
            self.goodwill = int(fact.value)
        elif name == e.Liabilities.name:
            self.liabilities = int(fact.value)
        elif name == e.CurrentLiabilities.name:
            self.currentLiabilities = int(fact.value)
        elif name in notesAndAccountsPayableTrade_ls:
            self.notesAndAccountsPayableTrade[name] = int(fact.value)
        elif name == e.NoncurrentLiabilities.name:
            self.noncurrentLiabilities = int(fact.value)
        elif name == e.NetAssets.name:
            self.netAssets = int(fact.value)
        elif name == e.ShareholdersEquity.name:
            self.shareholdersEquity = int(fact.value)
        elif name == e.RetainedEarnings.name:
            self.retainedEarnings = int(fact.value)
        elif name == e.TreasuryStock.name:
            self.treasuryStock = int(fact.value)
        elif name == e.ValuationAndTranslationAdjustments.name:
            self.valuationAndTranslationAdjustments = int(fact.value)
        elif name == e.NonControllingInterests.name:
            self.nonControllingInterests = int(fact.value)
        elif name == e.NetAssetsPerShareSummaryOfBusinessResults.name:
            self.BPS = float(fact.value)
        elif name in debt_list:
            self.add_value_to_interestBearingDebt(int(fact.value))
        else:
            print("Error: BS p_jp_parse")
        return True

    def p_us_parse(self,fact,isConsolidated) -> bool:
        e = self.US
        contextId = "CurrentYearInstant"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId = "CurrentYearInstant_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId:
            return False
        
        if name == e.TotalAssetsUSGAAPSummaryOfBusinessResults.name:
            self.assets = int(fact.value)
        elif name == e.EquityIncludingPortionAttributableToNonControllingInterestUSGAAPSummaryOfBusinessResults.name:
            self.netAssets = int(fact.value)
        elif name == e.EquityAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults.name:
            self.shareholdersEquity = int(fact.value)
        elif name == e.EquityAttributableToOwnersOfParentPerShareUSGAAPSummaryOfBusinessResults.name:
            self.BPS = float(fact.value)
        else:
            print("Error:プログラミングが間違えています。p_us_parse")
        return True

    def p_ifrs_parse(self,fact,isConsolidated) -> bool:
        e = self.IFRS
        contextId = "CurrentYearInstant"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId = "CurrentYearInstant_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId:
            return False
        
        debt_ls = [e.InterestBearingLiabilitiesCLIFRS.name,e.BondsAndBorrowingsCLIFRS.name,e.BondsPayableCLIFRS.name,e.BorrowingsCLIFRS.name,e.CurrentPortionOfLongTermBorrowingsCLIFRS.name,e.InterestBearingLiabilitiesNCLIFRS.name,e.BondsAndBorrowingsNCLIFRS.name,e.BondsPayableNCLIFRS.name,e.BorrowingsNCLIFRS.name]
        if name == e.AssetsIFRS.name:
            self.assets = int(fact.value)
        elif name == e.CurrentAssetsIFRS.name:
            self.currentAssets = int(fact.value)
        elif name == e.TradeAndOtherReceivablesCAIFRS.name or name == e.TradeAndOtherReceivables2CAIFRS.name or name == e.TradeAndOtherReceivables3CAIFRS.name:
            self.notesAndAccountsReceivableTrade = int(fact.value)
        elif name == e.InventoriesCAIFRS.name:
            self.inventories = int(fact.value)
        elif name == e.NonCurrentAssetsIFRS.name:
            self.noncurrentAssets = int(fact.value)
        elif name == e.GoodwillIFRS.name:
            self.goodwill = int(fact.value)
        elif name == e.LiabilitiesIFRS.name:
            self.liabilities  = int(fact.value)
        elif name == e.TotalCurrentLiabilitiesIFRS.name:
            self.currentLiabilities = int(fact.value)
        elif name == e.TradeAndOtherPayablesNCLIFRS.name or name == e.TradeAndOtherPayables2NCLIFRS.name or name == e.TradeAndOtherPayables3CLIFRS.name:
            self.notesAndAccountsPayableTrade = int(fact.value)
        elif name == e.NonCurrentLabilitiesIFRS.name:
            self.noncurrentLiabilities = int(fact.value)
        elif name == e.PropertyPlantAndEquipmentIFRS.name:
            self.propertyPlantAndEquipment = int(fact.value)
        elif name == e.EquityIFRS.name:
            self.netAssets  = int(fact.value)
        elif name == e.EquityAttributableToOwnersOfParentIFRS.name:
            self.shareholdersEquity = int(fact.value)
        elif name == e.RetainedEarningsIFRS.name:
            self.retainedEarnings  = int(fact.value)
        elif name == e.TreasurySharesIFRS.name:
            self.treasuryStock  = int(fact.value)
        elif name == e.NonControllingInterestsIFRS.name:
            self.nonControllingInterests  = int(fact.value)
        elif name == e.EquityToAssetRatioIFRSSummaryOfBusinessResults.name:
            self.BPS  = float(fact.value)
        elif name == e.TotalAssetsIFRSSummaryOfBusinessResults.name:
            self.assets  = int(fact.value)
        elif name == e.EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults.name:
            self.shareholdersEquity  = int(fact.value)
        elif name in debt_ls:
            self.add_value_to_interestBearingDebt(int(fact.value))
        else:
            print("Error: BS p_ifrs_parse")
        return True
    
    class JP(Enum):
        """日本基準"""
        Assets = auto()
        """資産"""
        CurrentAssets = auto()
        """流動資産"""

        NotesAndAccountsReceivableTradeAndContractAssets = auto()
        """受取手形、売掛金及び契約資産"""
        NotesAndAccountsReceivableTrade = auto()
        """受取手形及び売掛金"""
        NotesReceivableTrade = auto()
        """受取手形"""
        AccountsReceivableTrade = auto()
        """売掛金"""
        ContractAssets = auto()
        """契約資産"""
        AccountsReceivableInstallment = auto()
        """割賦売掛金"""
        ElectronicallyRecordedMonetaryClaimsOperatingCA = auto()
        """電子記録債券"""
        NotesReceivableAccountsReceivableFromCompletedConstructionContractsAndOtherCNS = auto()
        """建設業（売上債権）"""
        NotesReceivableAccountsReceivableFromCompletedConstructionContractsCNS = auto()
        """建設業（売上債権）"""
        AccountsReceivableFromCompletedConstructionContractsCNS = auto()
        """建設業（売上債権）"""

        Inventories = auto()
        """棚卸資産"""
        MerchandiseAndFinishedGoods = auto()
        """商品及び製品"""
        Merchandise = auto()
        """商品"""
        FinishedGoods = auto()
        """製品"""
        SemiFinishedGoods = auto()
        """半製品"""
        RawMaterials = auto()
        """原材料"""
        RawMaterialsAndSupplies = auto()
        """原材料及び貯蔵品"""
        WorkInProcess = auto()
        """仕掛品"""
        Supplies = auto()
        """貯蔵品"""

        NoncurrentAssets = auto()
        """固定資産"""
        PropertyPlantAndEquipment = auto()
        """有形固定資産"""
        DeferredAssets = auto()
        """繰延資産"""
        Goodwill = auto()
        """のれん"""
        Liabilities = auto()
        """負債"""
        CurrentLiabilities = auto()
        """流動負債"""

        NotesAndAccountsPayableTrade = auto()
        """支払手形及び買掛金"""
        NotesPayableTrade = auto()
        """支払手形"""
        AccountsPayableTrade = auto()
        """買掛金"""
        ElectronicallyRecordedObligationsOperatingCL = auto()
        """電子記録債務"""
        ContractLiabilities = auto()
        """契約債務"""
        NotesPayableAccountsPayableForConstructionContractsAndOtherCNS = auto()
        """建設業（仕入債務）"""
        NotesPayableAccountsPayableForConstructionContractsCNS = auto()
        """建設業（仕入債務）"""
        AccountsPayableForConstructionContractsCNS = auto()
        """建設業（仕入債務）"""

        NoncurrentLiabilities =auto()
        """固定負債"""
        NetAssets = auto()
        """純資産"""
        ShareholdersEquity = auto()
        """株主資本"""
        RetainedEarnings = auto()
        """利益剰余金"""
        TreasuryStock = auto()
        """自己株式"""
        ValuationAndTranslationAdjustments = auto()
        """その他包括利益累計額"""
        NonControllingInterests = auto()
        """非支配株主持分"""
        NetAssetsPerShareSummaryOfBusinessResults = auto()
        """BPS"""

        ShortTermBondsPayable = auto()
        """短期社債"""
        ShortTermLoansPayable = auto()
        """短期借入金"""
        CommercialPapersLiabilities = auto()
        """CP"""
        CurrentPortionOfBonds = auto()
        """1年内償還予定の社債"""
        CurrentPortionOfLongTermLoansPayable = auto()
        """1年内返済予定の長期借入金"""
        CurrentPortionOfConvertibleBonds = auto()
        """1年内償還予定の転換社債"""
        CurrentPortionOfBondsWithSubscriptionRightsToShares = auto()
        """1年内償還予定の新株予約権付社債"""
        BondsPayable = auto()
        """社債"""
        ConvertibleBonds = auto()
        """転換社債"""
        ConvertibleBondTypeBondsWithSubscriptionRightsToShares = auto()
        """転換社債型新株予約権付社債"""
        BondsWithSubscriptionRightsToSharesNCL = auto()
        """新株予約権付社債"""
        LongTermLoansPayable = auto()
        """長期借入金"""
    
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    class IFRS(Enum):
        """国際会計基準"""
        AssetsIFRS = auto()
        """資産"""
        CurrentAssetsIFRS = auto()
        """流動資産"""

        TradeAndOtherReceivablesCAIFRS = auto()
        """売上債権等"""
        TradeAndOtherReceivables2CAIFRS = auto()
        """売上債権等"""
        TradeAndOtherReceivables3CAIFRS = auto()
        """売上債権等"""
        InventoriesCAIFRS = auto()
        """棚卸資産"""
        NonCurrentAssetsIFRS = auto()
        """非流動資産"""
        PropertyPlantAndEquipmentIFRS = auto()
        """有形固定資産"""
        GoodwillIFRS = auto()
        """のれん"""
        LiabilitiesIFRS = auto()
        """負債"""
        TotalCurrentLiabilitiesIFRS = auto()
        """流動負債"""
        TradeAndOtherPayablesCLIFRS = auto()
        """仕入債務等"""
        TradeAndOtherPayables2CLIFRS = auto()
        """仕入債務等"""
        TradeAndOtherPayables3CLIFRS = auto()

        NonCurrentLabilitiesIFRS = auto()
        """非流動負債"""
        EquityIFRS = auto()
        """純資産"""
        EquityAttributableToOwnersOfParentIFRS = auto()
        """株主持分"""
        RetainedEarningsIFRS = auto()
        """利益剰余金"""
        TreasurySharesIFRS = auto()
        """自己株式"""
        NonControllingInterestsIFRS = auto()
        """非支配株主持分"""
        EquityToAssetRatioIFRSSummaryOfBusinessResults = auto()
        """BPS"""

        InterestBearingLiabilitiesCLIFRS = auto()
        """有利子負債"""
        BondsAndBorrowingsCLIFRS = auto()
        """社債及び借入金"""
        BondsPayableCLIFRS = auto()
        """社債"""
        BorrowingsCLIFRS = auto()
        """借入金"""
        CurrentPortionOfLongTermBorrowingsCLIFRS = auto()
        """1年内返済予定の長期借入金"""
        InterestBearingLiabilitiesNCLIFRS = auto()
        """有利子負債"""
        BondsAndBorrowingsNCLIFRS = auto()
        """社債及び借入金"""
        BondsPayableNCLIFRS = auto()
        """社債"""
        BorrowingsNCLIFRS = auto()
        """借入金"""
        
        TotalAssetsIFRSSummaryOfBusinessResults = auto()
        """総資産額"""
        EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults = auto()
        """親会社株主に帰属する持分"""

        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    class US(Enum):
        TotalAssetsUSGAAPSummaryOfBusinessResults = auto()
        """総資産"""
        EquityIncludingPortionAttributableToNonControllingInterestUSGAAPSummaryOfBusinessResults = auto()
        """純資産"""
        EquityAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults = auto()
        """株主資本"""
        EquityAttributableToOwnersOfParentPerShareUSGAAPSummaryOfBusinessResults = auto()
        """BPS"""

        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

class PL:
    def __init__(self) -> None:

        self.netSales = None
        """売上高"""
        self.revenue = None
        """売上収益"""
        self.operatingRevenue = None
        """営業収益"""
        self.grossProfit = None
        """売上総利益"""
        self.sellingGeneralAndAdministrativeExpenses = None
        "販管費"
        self.operatingIncome = None
        """営業利益"""
        self.operatingIncomeIFRS = None
        """営業利益（IFRS）"""
        self.ordinaryIncome = None
        """経常利益"""
        self.incomeBeforeIncomeTaxes = None
        """税引前当期純利益"""
        self.incomeTaxes = None
        """法人税等"""
        self.profitLoss = None
        """当期純利益"""
        self.profitLossAttributableToOwnersOfParent = None
        """親会社株主に帰属する当期純利益"""
        self.EPS = None
        """EPS"""

        self.ordinaryIncomeBNK = None
        """経常収益（銀行）"""
        self.operatingRevenueSEC = None
        """営業収益（証券）"""
        self.operatingIncomeINS = None
        """経常収益（保険）"""

    def main_parse(self,fact,account_standard:str,isConsolidated:str) -> bool:
        if fact.value == "":
            return False
        if account_standard == AccountingStandardClass.ifrs.value:
            return self.p_ifrs_parse(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.us_gaap.value:
            return self.p_us_parse(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.japan_gaap.value:
            return self.p_jp_parse(fact=fact,isConsolidated=isConsolidated)
        else:
            return False
    
    def cal_operaitigIncome_from_ifrs(self):
        if self.grossProfit != None and self.sellingGeneralAndAdministrativeExpenses != None:
            self.operatingIncome = self.grossProfit - self.sellingGeneralAndAdministrativeExpenses

    def p_jp_parse(self,fact,isConsolidated) -> bool:
        e = self.JP
        contextId = "CurrentYearDuration"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId = "CurrentYearDuration_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId:
            return False
        
        if name == e.NetSales.name:
            self.netSales = int(fact.value)
        elif name == e.Revenue.name:
            self.revenue = int(fact.value)
        elif name == e.OperatingRevenue1.name:
            self.operatingRevenue = int(fact.value)
        elif name == e.GrossProfit.name:
            self.grossProfit = int(fact.value)
        elif name == e.SellingGeneralAndAdministrativeExpenses.name:
            self.sellingGeneralAndAdministrativeExpenses = int(fact.value)
        elif name == e.OperatingIncome.name:
            self.operatingIncome = int(fact.value)
        elif name == e.OrdinaryIncome.name:
            self.ordinaryIncome = int(fact.value)
        elif name == e.IncomeBeforeIncomeTaxes.name:
            self.incomeBeforeIncomeTaxes = int(fact.value)
        elif name == e.IncomeTaxes.name:
            self.incomeTaxes = int(fact.value)
        elif name == e.ProfitLoss.name:
            self.profitLoss = int(fact.value)
        elif name == e.ProfitLossAttributableToOwnersOfParent.name:
            self.profitLossAttributableToOwnersOfParent = int(fact.value)
        elif name == e.BasicEarningsLossPerShareSummaryOfBusinessResults.name:
            self.EPS = float(fact.value)
        elif name == e.OrdinaryIncomeBNK.name:
            self.ordinaryIncomeBNK = int(fact.value)
        elif name == e.OperatingRevenueSEC.name:
            self.operatingRevenueSEC = int(fact.value)
        elif name == e.OperatingIncomeINS.name:
            self.operatingIncomeINS = int(fact.value)
        else:
            print("Error : PL >>> p_jp_parse")
        return True
            
    def p_us_parse(self,fact,isConsolidated) -> bool:
        e = self.US
        contextId = "CurrentYearDuration"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId = "CurrentYearDuration_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId:
            return False
        
        if name == e.RevenuesUSGAAPSummaryOfBusinessResults.name:
            self.netSales = int(fact.value)
        elif name == e.OperatingIncomeLossUSGAAPSummaryOfBusinessResults.name:
            self.operatingIncome = int(fact.value)
        elif name == e.ProfitLossBeforeTaxUSGAAPSummaryOfBusinessResults.name:
            self.incomeBeforeIncomeTaxes = int(fact.value)
        elif name == e.NetIncomeLossAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults.name:
            self.profitLossAttributableToOwnersOfParent = int(fact.value)
        elif name == e.BasicEarningsLossPerShareUSGAAPSummaryOfBusinessResults.name:
            self.EPS = float(fact.value)
        else:
            print("Error : PL >>> p_us_parse")
        return True
    
    def p_ifrs_parse(self,fact,isConsolidated) -> bool:
        e = self.IFRS
        contextId = "CurrentYearDuration"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId = "CurrentYearDuration_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId:
            return False
        
        if name == e.RevenueIFRS.name:
            self.revenue = int(fact.value)
        elif name == e.NetSalesIFRS.name:
            self.netSales = int(fact.value)
        elif name == e.Revenue2IFRS.name:
            self.operatingRevenue = int(fact.value)
        elif name == e.GrossProfitIFRS.name:
            self.grossProfit = int(fact.value)
        elif name == e.SellingGeneralAndAdministrativeExpensesIFRS.name:
            self.sellingGeneralAndAdministrativeExpenses = int(fact.value)
        elif name == e.OperatingProfitLossIFRS.name:
            self.operatingIncomeIFRS = int(fact.value)
        elif name == e.ProfitLossBeforeTaxIFRS.name:
            self.incomeBeforeIncomeTaxes = int(fact.value)
        elif name == e.IncomeTaxExpenseIFRS.name:
            self.incomeTaxes = int(fact.value)
        elif name == e.ProfitLossIFRS.name:
            self.profitLoss = int(fact.value)
        elif name == e.ProfitLossAttributableToOwnersOfParentIFRS.name:
            self.profitLossAttributableToOwnersOfParent = int(fact.value)
        elif name == e.BasicEarningsLossPerShareIFRSSummaryOfBusinessResults.name:
            self.EPS = float(fact.value)
        elif name == e.RevenueIFRSSummaryOfBusinessResults.name:
            self.revenue = int(fact.value)
        elif name == e.ProfitLossBeforeTaxIFRSSummaryOfBusinessResults.name:
            self.incomeBeforeIncomeTaxes = int(fact.value)
        elif name == e.ProfitLossIFRSSummaryOfBusinessResults.name:
            self.profitLoss = int(fact.value)
        elif name == e.ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults.name:
            self.profitLossAttributableToOwnersOfParent = int(fact.value)
        else:
            print("Error : PL >>> p_ifrs_parse")
        return True
    

    class JP(Enum):
        """損益計算書"""
        NetSales = auto()
        """売上高"""
        Revenue = auto()
        """売上収益"""
        OperatingRevenue1 = auto()
        """営業収益"""
        GrossProfit = auto()
        """売上総利益又は損失"""
        SellingGeneralAndAdministrativeExpenses = auto()
        """販管費"""
        OperatingIncome = auto()
        """営業利益又は損失"""
        OrdinaryIncome = auto()
        """経常利益又は損失"""
        IncomeBeforeIncomeTaxes = auto()
        """税引前当期純利益又は損失"""
        IncomeTaxes = auto()
        """法人税等"""
        ProfitLoss = auto()
        """当期純利益"""
        ProfitLossAttributableToOwnersOfParent = auto()
        """親会社株主に帰属する当期純利益又は損失"""
        BasicEarningsLossPerShareSummaryOfBusinessResults = auto()
        """EPS"""

        OrdinaryIncomeBNK = auto()
        """経常収益（銀行）"""
        OperatingRevenueSEC = auto()
        """営業収益（証券）"""
        OperatingIncomeINS = auto()
        """経常収益（保険）"""


        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    class IFRS(Enum):
        RevenueIFRS = auto()
        """売上収益"""
        NetSalesIFRS = auto()
        """売上高"""
        Revenue2IFRS = auto()
        """収益"""
        GrossProfitIFRS = auto()
        """売上総利益"""
        SellingGeneralAndAdministrativeExpensesIFRS = auto()
        """販管費"""
        OperatingProfitLossIFRS = auto()
        """営業利益"""
        ProfitLossBeforeTaxIFRS = auto()
        """税引前当期純利益"""
        IncomeTaxExpenseIFRS = auto()
        ProfitLossIFRS = auto()
        """当期純利益"""
        ProfitLossAttributableToOwnersOfParentIFRS = auto()
        """親会社株主持分当期純利益"""
        BasicEarningsLossPerShareIFRSSummaryOfBusinessResults = auto()
        """EPS"""

        RevenueIFRSSummaryOfBusinessResults = auto()
        """売上収益"""
        ProfitLossBeforeTaxIFRSSummaryOfBusinessResults = auto()
        """税引前当期純利益"""
        ProfitLossIFRSSummaryOfBusinessResults = auto()
        """当期純利益"""
        ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults = auto()
        """親会社株主に帰属する当期純利益"""

        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    class US(Enum):
        RevenuesUSGAAPSummaryOfBusinessResults = auto()
        """売上高"""
        OperatingIncomeLossUSGAAPSummaryOfBusinessResults = auto()
        """営業利益又は営業損失"""
        ProfitLossBeforeTaxUSGAAPSummaryOfBusinessResults = auto()
        """税引前当期純利益"""
        NetIncomeLossAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults = auto()
        """当社株主に帰属する当期純利益"""
        BasicEarningsLossPerShareUSGAAPSummaryOfBusinessResults = auto()
        """EPS"""
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

class CF:
    def __init__(self) -> None:
        self.netCashProvidedByUsedInOperatingActivities = None
        """営業活動によるキャッシュフロー"""
        self.netCashProvidedByUsedInInvestmentActivities = None
        """投資活動によるキャッシュフロー"""
        self.netCashProvidedByUsedInFinancingActivities = None
        """財務活動によるキャッシュフロー"""
        self.netIncreaseDecreaseInCashAndCashEquivalents = None
        """現金及び現金同等物の増減額"""
        self.cashAndCashEquivalents = None
        """現金及び現金同等物の残高"""
        self.depreciationAndAmortizationOpeCF = None
        """減価償却費"""
        self.amortizationOfGoodwillOpeCF = None
        """のれん償却額"""

    def main_parse(self,fact,account_standard:str,isConsolidated:str) -> bool:
        if fact.value == "":
            return False
        if account_standard == AccountingStandardClass.ifrs.value:
            return self.p_ifrs_parse(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.us_gaap.value:
            return self.p_us_parse(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.japan_gaap.value:
            return self.p_jp_parse(fact=fact,isConsolidated=isConsolidated)
        else:
            return False
    
    def p_jp_parse(self,fact,isConsolidated) -> bool:
        e = self.JP
        contextId_D = "CurrentYearDuration"
        contextId_I = "CurrentYearInstant"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId_D = "CurrentYearDuration_NonConsolidatedMember"
            contextId_I = "CurrentYearInstant_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId_D and fact.contextID != contextId_I:
            return False
                
        if name == e.NetCashProvidedByUsedInOperatingActivities.name:
            self.netCashProvidedByUsedInOperatingActivities = int(fact.value)
        elif name == e.NetCashProvidedByUsedInInvestmentActivities.name:
            self.netCashProvidedByUsedInInvestmentActivities = int(fact.value)
        elif name == e.NetCashProvidedByUsedInFinancingActivities.name:
            self.netCashProvidedByUsedInFinancingActivities = int(fact.value)
        elif name == e.NetIncreaseDecreaseInCashAndCashEquivalents.name:
            self.netIncreaseDecreaseInCashAndCashEquivalents = int(fact.value)
        elif name == e.CashAndCashEquivalents.name:
            self.cashAndCashEquivalents = int(fact.value)
        elif name == e.DepreciationAndAmortizationOpeCF.name:
            self.depreciationAndAmortizationOpeCF = int(fact.value)
        elif name == e.AmortizationOfGoodwillOpeCF.name:
            self.amortizationOfGoodwillOpeCF = int(fact.value)
        else:
            print("Error : CF >>> p_jp_parse")
        return True

    def p_us_parse(self,fact,isConsolidated) -> bool:
        e = self.US
        contextId_D = "CurrentYearDuration"
        contextId_I = "CurrentYearInstant"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId_D = "CurrentYearDuration_NonConsolidatedMember"
            contextId_I = "CurrentYearInstant_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId_D and fact.contextID != contextId_I:
            return False
                
        if name == e.CashFlowsFromUsedInOperatingActivitiesUSGAAPSummaryOfBusinessResults.name:
            self.netCashProvidedByUsedInOperatingActivities = int(fact.value)
        elif name == e.CashFlowsFromUsedInInvestingActivitiesUSGAAPSummaryOfBusinessResults.name:
            self.netCashProvidedByUsedInInvestmentActivities = int(fact.value)
        elif name == e.CashFlowsFromUsedInFinancingActivitiesUSGAAPSummaryOfBusinessResults.name:
            self.netCashProvidedByUsedInFinancingActivities = int(fact.value)
        elif name == e.CashAndCashEquivalentsUSGAAPSummaryOfBusinessResults.name:
            self.cashAndCashEquivalents = int(fact.value)
        else:
            print("Error : CF >>> p_jp_parse")
        return True
    
    def p_ifrs_parse(self,fact,isConsolidated) -> bool:
        e = self.IFRS
        contextId_D = "CurrentYearDuration"
        contextId_I = "CurrentYearInstant"
        tags = e.to_list()
        name = fact.concept.name
        if isConsolidated == "false":
            contextId_D = "CurrentYearDuration_NonConsolidatedMember"
            contextId_I = "CurrentYearInstant_NonConsolidatedMember"
        if name not in tags:
            return False
        if fact.contextID != contextId_D and fact.contextID != contextId_I:
            return False
                
        if name == e.NetCashProvidedByUsedInOperatingActivitiesIFRS.name:
            self.netCashProvidedByUsedInOperatingActivities = int(fact.value)
        elif name == e.NetCashProvidedByUsedInInvestingActivitiesIFRS.name:
            self.netCashProvidedByUsedInInvestmentActivities = int(fact.value)
        elif name == e.NetCashProvidedByUsedInFinancingActivitiesIFRS.name:
            self.netCashProvidedByUsedInFinancingActivities = int(fact.value)
        elif name == e.NetIncreaseDecreaseInCashAndCashEquivalentsIFRS.name:
            self.netIncreaseDecreaseInCashAndCashEquivalents = int(fact.value)
        elif name == e.CashAndCashEquivalentsIFRS.name:
            self.cashAndCashEquivalents = int(fact.value)
        elif name == e.DepreciationAndAmortizationOfIntangibleAssetsOpeCFIFRS.name:
            self.p_check_depreciation_ifrs(int(fact.value))
        elif name == e.DepreciationAndAmortizationOpeCFIFRS.name:
            self.p_check_depreciation_ifrs(int(fact.value))
        elif name == e.DepreciationExpenseOpeCFIFRS.name:
            self.p_check_depreciation_ifrs(int(fact.value))
        elif name == e.CashFlowsFromUsedInOperatingActivitiesIFRSSummaryOfBusinessResults.name:
            self.netCashProvidedByUsedInOperatingActivities = int(fact.value)
        elif name == e.CashFlowsFromUsedInInvestingActivitiesIFRSSummaryOfBusinessResults.name:
            self.netCashProvidedByUsedInInvestmentActivities = int(fact.value)
        elif name == e.CashFlowsFromUsedInFinancingActivitiesIFRSSummaryOfBusinessResults.name:
            self.netCashProvidedByUsedInFinancingActivities = int(fact.value)
        elif name == e.CashAndCashEquivalentsIFRSSummaryOfBusinessResults.name:
            self.cashAndCashEquivalents = int(fact.value)
        else:
            print("Error : CF >>> p_jp_parse")
        return True
    
    def p_check_depreciation_ifrs(self,value):
        if self.depreciationAndAmortizationOpeCF == None:
            self.depreciationAndAmortizationOpeCF = value
        elif self.depreciationAndAmortizationOpeCF < value:
            self.depreciationAndAmortizationOpeCF = value
        else:
            pass





    class JP(Enum):
        NetCashProvidedByUsedInOperatingActivities = auto()
        """営業活動によるキャッシュフロー"""
        NetCashProvidedByUsedInInvestmentActivities = auto()
        """投資活動によるキャッシュフロー"""
        NetCashProvidedByUsedInFinancingActivities = auto()
        """財務活動によるキャッシュフロー"""
        NetIncreaseDecreaseInCashAndCashEquivalents = auto()
        """現金及び現金同等物の増減額"""
        CashAndCashEquivalents = auto()
        """現金及び現金同等物の残高"""

        DepreciationAndAmortizationOpeCF = auto()
        """減価償却費"""
        AmortizationOfGoodwillOpeCF = auto()
        """のれん償却額"""
        
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    class IFRS(Enum):
        NetCashProvidedByUsedInOperatingActivitiesIFRS = auto()
        """営業活動によるキャッシュフロー"""
        NetCashProvidedByUsedInInvestingActivitiesIFRS = auto()
        """投資活動によるキャッシュフロー"""
        NetCashProvidedByUsedInFinancingActivitiesIFRS = auto()
        """財務活動によるキャッシュフロー"""
        NetIncreaseDecreaseInCashAndCashEquivalentsIFRS = auto()
        """現金及び現金同等物の増減額"""
        CashAndCashEquivalentsIFRS = auto()
        """現金及び現金同等物の残高"""

        DepreciationAndAmortizationOpeCFIFRS = auto()
        """減価償却費及び償却費"""
        DepreciationAndAmortizationOfIntangibleAssetsOpeCFIFRS = auto()
        """減価償却費及び無形資産償却費"""
        DepreciationExpenseOpeCFIFRS = auto()
        """減価償却費"""

        CashFlowsFromUsedInOperatingActivitiesIFRSSummaryOfBusinessResults = auto()
        """営業活動によるキャッシュフロー"""

        CashFlowsFromUsedInInvestingActivitiesIFRSSummaryOfBusinessResults = auto()
        """投資活動によるキャッシュフロー"""

        CashFlowsFromUsedInFinancingActivitiesIFRSSummaryOfBusinessResults = auto()
        """財務活動によるキャッシュフロー"""

        CashAndCashEquivalentsIFRSSummaryOfBusinessResults = auto()
        """ 現金及び現金同等物"""


        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    class US(Enum):
        CashFlowsFromUsedInOperatingActivitiesUSGAAPSummaryOfBusinessResults = auto()
        """営業活動によるキャッシュフロー"""
        CashFlowsFromUsedInInvestingActivitiesUSGAAPSummaryOfBusinessResults = auto()
        """投資活動によるキャッシュフロー"""
        CashFlowsFromUsedInFinancingActivitiesUSGAAPSummaryOfBusinessResults = auto()
        """財務活動によるキャッシュフロー"""
        CashAndCashEquivalentsUSGAAPSummaryOfBusinessResults = auto()
        """現金及び現金同等物"""

        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

class OtherData:
    def __init__(self) -> None:
        self.numOfTotalShares = None
        """発行済み株式数"""
        self.numOfTreasuryShare = None
        """自己株式数"""
        self.dividendPaidPerShare = None
        """１株当たり配当額"""
        self.capitalExpendituresOverviewOfCapitalExpendituresEtc = None
        """設備投資額"""
        self.researchAndDevelopmentExpensesResearchAndDevelopmentActivities = None
        """研究開発費"""
        self.numberOfEmployees = None
        """従業員数"""

    def main_parse(self,fact) -> bool:
        if fact.value == "":
            return False
        e = self.OtherData_Tag
        name = fact.concept.name
        if name == e.NumberOfIssuedSharesAsOfFiscalYearEndIssuedSharesTotalNumberOfSharesEtc.name and fact.contextID == "FilingDateInstant":
           self.numOfTotalShares = int(fact.value)
        elif name == e.TotalNumberOfSharesHeldTreasurySharesEtc.name and fact.contextID == "CurrentYearInstant":
            self.numOfTreasuryShare = int(fact.value)
        elif name == e.DividendPaidPerShareSummaryOfBusinessResults.name and fact.contextID == "CurrentYearDuration_NonConsolidatedMember":
            self.dividendPaidPerShare = float(fact.value)
        elif name == e.CapitalExpendituresOverviewOfCapitalExpendituresEtc.name and fact.contextID == "CurrentYearDuration":
            self.capitalExpendituresOverviewOfCapitalExpendituresEtc = int(fact.value)
        elif name == e.ResearchAndDevelopmentExpensesResearchAndDevelopmentActivities.name and fact.contextID == "CurrentYearDuration":
            self.researchAndDevelopmentExpensesResearchAndDevelopmentActivities = int(fact.value)
        elif name == e.NumberOfEmployees.name and fact.contextID == "CurrentYearInstant":
            self.numberOfEmployees = int(fact.value)
        else:
            return False
        return True

    class OtherData_Tag(Enum):
        NumberOfIssuedSharesAsOfFiscalYearEndIssuedSharesTotalNumberOfSharesEtc = auto()
        """発行済み株式数"""
        TotalNumberOfSharesHeldTreasurySharesEtc = auto()
        """自己株式数"""
        DividendPaidPerShareSummaryOfBusinessResults = auto()
        """１株当たり配当額"""
        CapitalExpendituresOverviewOfCapitalExpendituresEtc = auto()
        """設備投資額"""
        ResearchAndDevelopmentExpensesResearchAndDevelopmentActivities = auto()
        """研究開発"""
        NumberOfEmployees = auto()
        """従業員数"""
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

class FS_HTML_Data:
    def __init__(self) -> None: 
        self.bs_html = None
        self.pl_html = None
        self.cf_html = None

    class ElementName(Enum):
        ConsolidatedBalanceSheetTextBlock = auto()
        """貸借対照表（日本連結）"""
        BalanceSheetTextBlock = auto()
        """貸借対照表（日本非連結）"""
        ConsolidatedBalanceSheetUSGAAPTextBlock = auto()
        """貸借対照表（米国）"""
        ConsolidatedStatementOfFinancialPositionIFRSTextBlock = auto()
        """貸借対照表（IFRS）"""
        ConsolidatedStatementOfIncomeTextBlock = auto()
        """損益計算書（日本連結）"""
        StatementOfIncomeTextBlock = auto()
        """損益計算書（日本非連結）"""
        ConsolidatedStatementOfIncomeUSGAAPTextBlock = auto()
        """損益計算書（米国）"""
        ConsolidatedStatementOfProfitOrLossIFRSTextBlock = auto()
        """損益計算書（IFRS）"""
        ConsolidatedStatementOfCashFlowsTextBlock = auto()
        """キャッシュフロー計算書（日本連結）"""
        StatementOfCashFlowsTextBlock = auto()
        """キャッシュフロー計算書（日本非連結）"""
        ConsolidatedStatementOfCashFlowsUSGAAPTextBlock = auto()
        """キャッシュフロー計算書（米国）"""
        ConsolidatedStatementOfCashFlowsIFRSTextBlock = auto()
        """キャッシュフロー計算書（IFRS）"""
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

    def main_parse(self,fact,account_standard:str,isConsolidated:str) -> bool:
        if fact.value == "":
            return False
        if account_standard == AccountingStandardClass.japan_gaap.value:
            return self.p_parse_jp(fact=fact,isConsolidated=isConsolidated)
        elif account_standard == AccountingStandardClass.ifrs.value:
            return self.p_parse_ifrs(fact=fact)
        elif account_standard == AccountingStandardClass.us_gaap.value:
            return self.p_parse_us(fact=fact)
        else:
            return False
    
    def p_parse_jp(self,fact,isConsolidated):
        name = fact.concept.name
        e = self.ElementName
        if isConsolidated == "true":
            if name == e.ConsolidatedBalanceSheetTextBlock.name:
                self.bs_html = self.html_encode(fact.value)
            elif name == e.ConsolidatedStatementOfIncomeTextBlock.name:
                self.pl_html = self.html_encode(fact.value)
            elif name == e.ConsolidatedStatementOfCashFlowsTextBlock.name:
                self.cf_html = self.html_encode(fact.value)
            else:
                return False
        else:
            if name == e.ConsolidatedBalanceSheetUSGAAPTextBlock.name:
                self.bs_html = self.html_encode(fact.value)
            elif name == e.StatementOfIncomeTextBlock.name:
                self.pl_html = self.html_encode(fact.value)
            elif name == e.StatementOfCashFlowsTextBlock.name:
                self.cf_html = self.html_encode(fact.value)
            else:
                return False
        return True
    
    def p_parse_ifrs(self,fact):
        name = fact.concept.name
        element = self.ElementName
        if name == element.ConsolidatedStatementOfFinancialPositionIFRSTextBlock.name:
            self.bs_html = self.html_encode(fact.value)
        elif name == element.ConsolidatedStatementOfProfitOrLossIFRSTextBlock.name:
            self.pl_html = self.html_encode(fact.value)
        elif name == element.ConsolidatedStatementOfCashFlowsIFRSTextBlock.name:
            self.cf_html = self.html_encode(fact.value)
        else:
            return False
        return True

    def p_parse_us(self,fact):
        name = fact.concept.name
        element = self.ElementName
        if name == element.ConsolidatedBalanceSheetUSGAAPTextBlock.name:
            self.bs_html = self.html_encode(fact.value)
        elif name == element.ConsolidatedStatementOfIncomeUSGAAPTextBlock.name:
            self.pl_html = self.html_encode(fact.value)
        elif name == element.ConsolidatedStatementOfCashFlowsUSGAAPTextBlock.name:
            self.cf_html = self.html_encode(fact.value)
        else:
            return False

        return True

    def html_encode(self,html:str) -> str:
        soup = BeautifulSoup(html)
        return(str(soup))

class Company_HTML_Data:
    def __init__(self) -> None:   
        self.history = None
        self.descriptionOfBusiness = None
        self.overviewOfAffiliatedEntities = None
        self.infoAboutEmployees = None
        self.bizPolicy = None
        self.bizRisks = None
        self.analysis = None
        self.researchAndDevelopmentActivities = None
        self.overviewOfCapitalExpenditures = None
        self.dividendPolicy = None
        self.majorShareholders = None
        self.segmentInfo = None

    def main_parse(self,fact) -> bool:
        if fact.value == "":
            return False
        name = fact.concept.name
        element = self.ElementName
        if name == element.CompanyHistoryTextBlock.name:
            self.history = self.html_tprocessing(fact.value)
        elif name == element.DescriptionOfBusinessTextBlock.name:
            self.descriptionOfBusiness = self.html_tprocessing(fact.value)
        elif name == element.OverviewOfAffiliatedEntitiesTextBlock.name:
            self.overviewOfAffiliatedEntities = self.html_tprocessing(fact.value)
        elif name == element.InformationAboutEmployeesTextBlock.name:
            self.infoAboutEmployees = self.html_tprocessing(fact.value)
        elif name == element.BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock.name:
            self.bizPolicy = self.html_tprocessing(fact.value)
        elif name == element.BusinessRisksTextBlock.name:
            self.bizRisks = self.html_tprocessing(fact.value)
        elif name == element.ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock.name:
            self.analysis = self.html_tprocessing(fact.value)
        elif name == element.ResearchAndDevelopmentActivitiesTextBlock.name:
            self.researchAndDevelopmentActivities = self.html_tprocessing(fact.value)
        elif name == element.OverviewOfCapitalExpendituresEtcTextBlock.name:
            self.overviewOfCapitalExpenditures = self.html_tprocessing(fact.value)
        elif name == element.DividendPolicyTextBlock.name:
            self.dividendPolicy = self.html_tprocessing(fact.value)
        elif name == element.MajorShareholdersTextBlock.name:
            self.majorShareholders = self.html_tprocessing(fact.value)
        elif name == element.NotesSegmentInformationEtcConsolidatedFinancialStatementsTextBlock.name:
            self.segmentInfo = self.html_tprocessing(fact.value)
        else:
            return False
        return True

    def html_tprocessing(self,html:str) -> str:
        soup = BeautifulSoup(html)
        for tag in soup.find_all(style=True):
            tag.attrs.clear()
            if tag.name == "table":
                tag.attrs["border"] = 1
                tag.attrs["style"] = "border-collapse: collapse"

        return(str(soup))

    class ElementName(Enum):
        CompanyHistoryTextBlock = auto()
        """沿革"""
        DescriptionOfBusinessTextBlock = auto()
        """事業の内容"""
        OverviewOfAffiliatedEntitiesTextBlock = auto()
        """関係会社の状況"""
        InformationAboutEmployeesTextBlock = auto()
        """従業員の状況"""
        BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock = auto()
        """経営方針"""
        BusinessRisksTextBlock = auto()
        """事業などのリスク"""
        ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock = auto()
        """経営者による分析"""
        ResearchAndDevelopmentActivitiesTextBlock = auto()
        """研究開発活動"""
        OverviewOfCapitalExpendituresEtcTextBlock = auto()
        """設備投資等の概要"""
        DividendPolicyTextBlock = auto()
        """配当政策"""
        MajorShareholdersTextBlock = auto()
        """大株主の状況"""
        NotesSegmentInformationEtcConsolidatedFinancialStatementsTextBlock = auto()
        """セグメント情報等"""
        @classmethod
        def to_list(self) -> list:
            """列挙型の要素をリスト化する"""
            return (self._member_names_)

class FinIndex:
    def __init__(self) -> None:
        ##主に安全性
        self.currentRatio = None
        """流動比率"""
        self.shortTermLiquidity = None
        """手元流動性比率"""
        self.fixedAssetsToNetWorth = None
        """固定比率"""
        self.fixedAssetToFixedLiabilityRatio = None
        """固定長期適合率"""
        self.equityRatio = None
        """自己資本比率"""
        self.debtEquityRatio = None
        """DEレシオ"""
        self.netDebt = None
        """ネット有利子負債"""
        self.netDebtEquityRation = None
        """ネットDEレシオ"""
        self.dependedDebtRatio = None
        """有利子負債依存度"""

        ##主に収益性
        self.grossProfitMargin = None
        """粗利率"""
        self.operatingIncomeMargin = None
        """営業利益率"""
        self.ordinaryIncomeMargin = None
        """経常利益率"""
        self.netProfitMargin = None
        """純利益率"""
        self.netProfitAttributeOfOwnerMargin = None
        """親会社株主に帰属する当期純利益率"""
        self.EBITDA = None
        """EBITDA"""
        self.EBITDAInterestBearingDebtRatio = None
        """EBITDA有利子負債倍率"""
        self.effectiveTaxRate = None
        """実効税率"""
        self.ROIC = None
        """ROIC"""
        self.ROE = None
        """ROE"""
        self.ROA = None

        ##主に効率性
        self.totalAssetsTurnover = None
        """総資産回転率"""
        self.receivablesTurnover = None
        """売上債権回転率"""
        self.inventoryTurnover = None
        """棚卸資産回転率"""
        self.payableTurnover = None
        """仕入債務回転率"""
        self.tangibleFixedAssetTurnover = None
        """有形固定資産回転率"""
        self.CCC = None
        """キャッシュ・コンバージョン・サイクル"""

        ##主にキャッシュフローによる分析指標
        self.netSalesOperatingCFRatio = None
        """売上営業CF比率"""
        self.equityOperatingCFRatio = None
        """自己資本営業CF比率"""
        self.operatingCFCurrentLiabilitiesRatio = None
        """CF版当座比率"""
        self.operatingCFDebtRatio = None
        """営業CF対有利子負債"""
        self.fixedInvestmentOperatingCFRatio = None
        """設備投資比率"""


    def cal_data(self,core:CoreData,detail:DetailData):
        netSales = self.p_check_netsales(core=core,detail=detail)
        operatingIncome = self.p_check_operatingIncome(core=core,detail=detail)
        equity = self.p_cal_shareholdersEquity(core=core,detail=detail)
        netProfit = None
        if core.WhetherConsolidatedFinancialStatementsArePreparedDEI == "true":
            netProfit = detail.pl.profitLossAttributableToOwnersOfParent
        else:
            netProfit = detail.pl.profitLoss
        
        interestBearingDebt = 0
        if detail.bs.interestBearingDebt != None:
            interestBearingDebt = detail.bs.interestBearingDebt


        try:
            self.currentRatio = detail.bs.currentAssets / detail.bs.currentLiabilities
        except:pass 
        try:
            self.shortTermLiquidity = detail.cf.cashAndCashEquivalents / netSales
        except:pass 
        try:
            self.fixedAssetsToNetWorth = detail.bs.noncurrentAssets / equity
        except:pass 
        try:
            self.fixedAssetToFixedLiabilityRatio = detail.bs.noncurrentAssets / (equity + detail.bs.noncurrentLiabilities)
        except:pass 
        try:
            self.equityRatio = equity / detail.bs.assets
        except:pass 
        try:
            self.debtEquityRatio = interestBearingDebt / equity
        except:pass 
        try:
            self.netDebt = interestBearingDebt - detail.cf.cashAndCashEquivalents
        except:pass 
        try:
            self.netDebtEquityRation = self.netDebt / equity
        except:pass 
        try:
            self.dependedDebtRatio = interestBearingDebt / detail.bs.assets
        except:pass
        try:
            self.grossProfitMargin = detail.pl.grossProfit / netSales
        except:pass
        try:
            self.operatingIncomeMargin = operatingIncome / netSales
        except:pass
        try:
            self.ordinaryIncomeMargin = detail.pl.ordinaryIncome / netSales
        except:pass
        try:
            self.netProfitMargin = detail.pl.profitLoss / netSales
        except:pass
        try:
            self.netProfitAttributeOfOwnerMargin = detail.pl.profitLossAttributableToOwnersOfParent / netSales
        except:pass
        try:
            self.p_cal_EBITDA(core,detail,operatingIncome)
        except:pass
        try:
            self.EBITDAInterestBearingDebtRatio = self.netDebt / self.EBITDA
        except:pass
        try:
            self.effectiveTaxRate = 1 - (detail.pl.profitLoss / detail.pl.incomeBeforeIncomeTaxes)
        except:pass
        try:
            self.ROIC = (operatingIncome - detail.pl.incomeTaxes) / (interestBearingDebt + equity)
        except:pass
        try:
            self.ROE = netProfit / equity
        except:pass
        try:
            self.ROA = netProfit / detail.bs.assets
        except:
            pass
        try:
            self.totalAssetsTurnover = netSales / detail.bs.assets
        except:pass
        try:
            self.receivablesTurnover = netSales / detail.bs.notesAndAccountsReceivableTrade
        except:pass
        try:
            if detail.pl.grossProfit == None:
                self.inventoryTurnover = netSales / detail.bs.inventories
            else:
                self.inventoryTurnover = (netSales - detail.pl.grossProfit) / detail.bs.inventories
        except:pass
        try:
            if detail.pl.grossProfit == None:
                self.payableTurnover = netSales / detail.bs.notesAndAccountsPayableTrade
            else:
                self.payableTurnover = (netSales - detail.pl.grossProfit) / detail.bs.notesAndAccountsPayableTrade
        except:pass
        try:
            self.tangibleFixedAssetTurnover = netSales / detail.bs.propertyPlantAndEquipment
        except:pass
        try:
            self.CCC = (365 / self.receivablesTurnover) + (365 / self.inventoryTurnover) - (365 / self.payableTurnover)
        except:pass
        try:
            self.netSalesOperatingCFRatio = detail.cf.netCashProvidedByUsedInOperatingActivities / netSales
        except:pass
        try:
            self.equityOperatingCFRatio = detail.cf.netCashProvidedByUsedInOperatingActivities / equity
        except:pass
        try:
            self.operatingCFCurrentLiabilitiesRatio = detail.cf.netCashProvidedByUsedInOperatingActivities / detail.bs.currentLiabilities
        except:pass
        try:
            self.operatingCFDebtRatio = interestBearingDebt / detail.cf.netCashProvidedByUsedInOperatingActivities
        except:pass
        try:
            self.fixedInvestmentOperatingCFRatio = detail.cf.netCashProvidedByUsedInOperatingActivities / detail.other.capitalExpendituresOverviewOfCapitalExpendituresEtc
        except:pass

    def p_check_netsales(self,core:CoreData,detail:DetailData):
        industryCode = None
        if core.WhetherConsolidatedFinancialStatementsArePreparedDEI == "true":
            industryCode = core.IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI
        else:
            industryCode = core.IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI
        
        if industryCode == IndustryCode.BNK.name:
            return detail.pl.ordinaryIncomeBNK
        elif industryCode == IndustryCode.INS.name:
            return detail.pl.operatingIncomeINS
        elif industryCode == IndustryCode.SEC.name:
            return detail.pl.operatingRevenueSEC

        ls = [detail.pl.netSales,detail.pl.operatingRevenue,detail.pl.revenue]
        result = None
        for content in ls:
            if result == None:
                result = content
            elif content != None and result < content:
                result = content
        
        return result

    def p_check_operatingIncome(self,core:CoreData,detail:DetailData):
        if core.AccountingStandardsDEI == AccountingStandardClass.ifrs:
            if detail.pl.operatingIncomeIFRS != None:
                return detail.pl.operatingIncomeIFRS
            else:
                return detail.pl.operatingIncome
        else:
            return detail.pl.operatingIncome
            
    def p_cal_shareholdersEquity(self,core:CoreData,detail:DetailData):
        if core.AccountingStandardsDEI == AccountingStandardClass.japan_gaap.value:
            try:
                return detail.bs.shareholdersEquity + detail.bs.valuationAndTranslationAdjustments
            except:
                return detail.bs.shareholdersEquity
        else:
            return detail.bs.shareholdersEquity
    
    def p_cal_EBITDA(self,core:CoreData,detail:DetailData,operatingIncome):
        if detail.cf.amortizationOfGoodwillOpeCF == None:
            try:
                self.EBITDA = operatingIncome + detail.cf.depreciationAndAmortizationOpeCF
            except:pass
        else:
            try:
                self.EBITDA = operatingIncome + detail.cf.depreciationAndAmortizationOpeCF + detail.cf.amortizationOfGoodwillOpeCF
            except:pass

            

class SaveCompanyDataToFireStore:
    CompanyCorePath = None
    finCorePath = None
    bsPath = None
    plPath = None
    cfPath = None
    otherPath = None
    fsHTMLPath = None
    companyHTMLPath = None
    finIndexPath = None

    def __init__(self,company_core_path,fin_core_path,bs_path,pl_path,cf_path,other_path,fsHTML_path,companyHTML_path,finIndex_path) -> None:
        self.companyCorePath = company_core_path
        self.finCorePath = fin_core_path
        self.bsPath = bs_path
        self.plPath = pl_path
        self.cfPath = cf_path
        self.otherPath = other_path
        self.fsHTMLPath = fsHTML_path
        self.companyHTMLPath = companyHTML_path
        self.finIndexPath = finIndex_path

    def save_data(self,path,dict_data):
        path.set(dict_data,merge=True)

    def save_company_data(self,coreData:CoreData,detailData:DetailData,fin_index:FinIndex,formCode):
        #self.p_save_company_core_data(coreData=coreData)
        #self.p_save_fin_core_data(coreData=coreData,formCode=formCode)
        self.save_data(path=self.bsPath,dict_data=detailData.bs.__dict__)
        #self.save_data(path=self.plPath,dict_data=detailData.pl.__dict__)
        #self.save_data(path=self.cfPath,dict_data=detailData.cf.__dict__)
        #self.save_data(path=self.otherPath,dict_data=detailData.other.__dict__)
        #self.save_data(path=self.fsHTMLPath,dict_data=detailData.fs_html.__dict__)
        #self.save_data(path=self.companyHTMLPath,dict_data=detailData.company_html.__dict__)
        self.save_data(path=self.finIndexPath,dict_data=fin_index.__dict__)
    
    def p_save_company_core_data(self,coreData:CoreData):
        self.companyCorePath.set({
            u'JCN':coreData.JCN,
            u'EDINETCode':coreData.EDINETCodeDEI,
            u'companyNameInJP':coreData.FilerNameInJapaneseDEI,
            u'companuNameInENG':coreData.FilerNameInEnglishDEI,
            u'secCode':coreData.SecurityCodeDEI,
            u'lastModified':datetime.datetime.now(tz=datetime.timezone.utc),
            u'simpleCompanyNameInJP':coreData.simpleCompanyNameInJP,
        },merge=True)
    
    def p_save_fin_core_data(self,coreData:CoreData,formCode:str):
        industry_code = ""
        if coreData.WhetherConsolidatedFinancialStatementsArePreparedDEI == "true":
            industry_code = str(coreData.IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI).upper()
        else:
            industry_code = str(coreData.IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI).upper()
        self.finCorePath.set({
            u'fiscalYear':coreData.FiscalYearCoverPage,
            u'accountingStandard':coreData.AccountingStandardsDEI,
            u'ordinanceCode':u'010',
            u'formCode':formCode,
            u'industryCodeDEI':industry_code,
            u'whetherConsolidated':coreData.WhetherConsolidatedFinancialStatementsArePreparedDEI,
            u'currentFiscalYearStartDate':coreData.CurrentFiscalYearStartDateDEI,
            u'currentPeriodEndDate':coreData.CurrentPeriodEndDateDEI,
            u'currentFiscalYearEndDate':coreData.CurrentFiscalYearEndDateDEI,
            u'typeOfCurrentPeriod':coreData.TypeOfCurrentPeriodDEI
        },merge=True)



