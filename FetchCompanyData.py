from enum import Enum
import os
import shutil
from arelle import Cntlr
import datetime
from dateutil import relativedelta
import requests
import glob
import csv
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from AccountClass import AccountingStandardClass,CoreData,FinIndex,IndustryCode
cred = credentials.Certificate('C://Users//taku3//Dropbox//Biz//FetchCompanyData//corporateanalysishubapp-firebase-adminsdk-n8sd4-07e702dbc7.json')




search_companyName_dict = {}
search_secCode_dict = {}

class FetchXBRLFileClass:
    class SearchParameter:
        class formCodeType(Enum):
            YHO = "030000"
            YHO_T = "030001"
            YNPO = "043000"
            YNPO_T = "043001"
        mode = None
        start_date = None
        end_date = None
        secCode_list = None
        formCode:formCodeType = None
        def __init__(self,mode,s_date,e_date,secCode_list,formCode:formCodeType) -> None:
            self.mode = mode
            self.start_date = s_date
            self.end_date = e_date
            self.secCode_list = secCode_list
            self.formCode = formCode
    class ResultData:
        jcn_str_dict = {}
        secCode_str_dict = {}
        doc_id_list = []

        def setData(self,jcn,sec,docID) -> None:
            self.jcn_str_dict = jcn
            self.secCode_str_dict = sec
            self.doc_id_list = docID

    #ENINET API
    EDINET_API_ENDPOINT_BASE:str = "https://disclosure.edinet-fsa.go.jp/api/v1/"
    
    def edinetApiDocumentEndpoint_private(self,documentID:str) -> str:
        '''書類取得APIエンドポイント（リクエストURL）'''
        #typeは1で固定する
        edinetApiDocumentEndpoint_private = self.EDINET_API_ENDPOINT_BASE + F"documents/{documentID}?type=1"
        return edinetApiDocumentEndpoint_private
    
    def edinetApiDocumentListEndpoint_private(self,requestListDate:datetime.date,requestListResponseType:int) -> str:
        '''書類一覧APIエンドポイント（リクエストURL）'''
        edinetApiDocumentListEndpoint_private = self.EDINET_API_ENDPOINT_BASE + F"documents.json?date={requestListDate}&type={requestListResponseType}"
        return edinetApiDocumentListEndpoint_private
    
    def makeDayList_private(self,startDate,endDate) -> list:
        '''期間を指定して返す'''
        period = endDate - startDate
        period = int(period.days)
        if period == 0:
            period = 1
        dayList = []
        for i in range(period):
            day = startDate + datetime.timedelta(days=i)
            dayList.append(day)
            if i == period - 1:#期間両入
                dayList.append(day + datetime.timedelta(days=1))
        return dayList
    
    def makeDocIdList_private(self,dayList:list,parameter:SearchParameter) -> ResultData:
        '''
        期間内の条件に当てはまる書類IDをリストにして返す　　secCode=すべて検索の場合　None

        '''
        result = self.ResultData()
        docIDList = []
        finish_count = len(dayList) - 1
        jcn_str_dict = {}
        secCode_str_dict = {}
        for index,day in enumerate(dayList):
            url = self.edinetApiDocumentListEndpoint_private(day,2)
            res = requests.get(url)
            jsonData = res.json()
            if jsonData["metadata"]["status"] != "200":
                tmp = jsonData["metadata"]["status"]
                print(F"{day}:{tmp}")
            elif parameter.secCode_list == None:
                for num in range(0,jsonData["metadata"]["resultset"]["count"]):
                    ordinanceCode = jsonData["results"][num]["ordinanceCode"]
                    formCode = jsonData["results"][num]["formCode"]
                    secCode = jsonData["results"][num]["secCode"]
                    #上場のみ有価証券報告書
                    if ordinanceCode == "010" and formCode == parameter.formCode.value:
                        jcn_str_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["JCN"]
                        secCode_str_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["secCode"]
                        docID = jsonData["results"][num]["docID"]
                        docIDList.append(docID)
            else:
                for num in range(0,jsonData["metadata"]["resultset"]["count"]):
                    ordinanceCode = jsonData["results"][num]["ordinanceCode"]
                    formCode = jsonData["results"][num]["formCode"]
                    secCode = jsonData["results"][num]["secCode"]
                    #上場のみ有価証券報告書
                    if ordinanceCode == "010" and formCode == parameter.formCode.value and secCode in parameter.secCode_list:
                        jcn_str_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["JCN"]
                        secCode_str_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["secCode"]
                        docID = jsonData["results"][num]["docID"]
                        docIDList.append(docID)

            
            print(f"search_doc : {index}/{finish_count}")
        print("検索が終了しました")
        result.setData(jcn=jcn_str_dict,sec=secCode_str_dict,docID=docIDList)
        return result

    def downloadXbrlInZip_private(self,docList:list):
        '''docListのXBRLをダウンロードする'''
        print(len(docList))
        finish_count = len(docList) - 1
        for index, docID in enumerate(docList):
            url = self.edinetApiDocumentEndpoint_private(docID)
            filename = "G:XBRL_For_Python_Parse//" + docID + ".zip"
            res = requests.get(url)
            if res.status_code == 200:
                with open(filename,"wb") as file:
                    for chunk in res.iter_content(chunk_size=1024):
                        file.write(chunk)
            else:
                print("失敗しました")
                print(res.status_code)
            print(f"download : {index}/{finish_count}")        
        print("ダウンロードが終了しました")

    def unzip_File_private(self,zipDir):
        '''zipFileを展開しxbrlFileを取り出す'''
        folders = []
        zip_Files = glob.glob(os.path.join(zipDir,'*.zip'))
        for index, zip_File in enumerate(zip_Files):#index除かない！！
            basename_without_zip = os.path.splitext(os.path.basename(zip_File))[0]
            #with zipfile.ZipFile(zip_File) as zip_f:
            try:
                shutil.unpack_archive(zip_File,f'{zipDir}//{basename_without_zip}')
            except:
                self.downloadXbrlInZip_private(docList=[basename_without_zip])
                shutil.unpack_archive(zip_File,f'{zipDir}//{basename_without_zip}')
            folders.append(basename_without_zip)
                #zip_f.extractall(zipDir)
                #zip_f.close()
        #xbrl_files = glob.glob(xblrFileExpressions)
        #不使用なzipFileを削除する
        removeZipfiles = glob.glob(zipDir + "*.zip")
        for file in removeZipfiles:
            os.remove(file)
        return folders
    
    def fetchXbrlFile(self,parameter:SearchParameter) -> ResultData:
        '''期間を指定しその期間の書類を取得し、ファイルPathのリストを返す　mode => 0[パソコン上]　1[APIダウンロード]  startDateとendDateが両方 None の時５年間　　secCodesが None のとき全部検索'''

        s_date = parameter.start_date
        e_date = parameter.end_date
        ################
        if parameter.start_date == None or parameter.end_date == None:
            e_date = datetime.date.today()
            s_date = datetime.date(year=e_date.year - 5,month=e_date.month,day=e_date.day)
        ################
        result = self.ResultData()
        path = "G:XBRL_For_Python_Parse////"
        if parameter.mode == 0:
            files = os.listdir(path)
            dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
            dayList = self.makeDayList_private(s_date,e_date)
            result = self.makeDocIdList_private(dayList,parameter=parameter)
            result.doc_id_list = dir
            return result
        elif parameter.mode == 1:
            dayList = self.makeDayList_private(s_date,e_date)
            result = self.makeDocIdList_private(dayList,parameter=parameter)
            self.downloadXbrlInZip_private(result.doc_id_list)
            self.unzip_File_private(path)
            return result


'''改善版'''
class ParseXBRLFileClass():
    def makeContextIDDict(self,TypeOfCurrentPeriodDEI,WhetherConsolidatedFinancialStatementsArePreparedDEI) -> dict:
        currentInstant = None
        currentDuration = None
        if WhetherConsolidatedFinancialStatementsArePreparedDEI == "true":
            if TypeOfCurrentPeriodDEI == "FY":
                currentInstant = "CurrentYearInstant"
                currentDuration = "CurrentYearDuration"
            elif TypeOfCurrentPeriodDEI == "HY":
                currentInstant = "InterimInstant"
                currentDuration = "InterimDuration"
            elif TypeOfCurrentPeriodDEI == "Q1" or "Q2" or "Q3" or "Q4" or "Q5":
                currentInstant = "CurrentQuarterInstant"
                currentDuration = "CurrentYTDDuration"
        elif WhetherConsolidatedFinancialStatementsArePreparedDEI == "false":
            if TypeOfCurrentPeriodDEI == "FY":
                currentInstant = "CurrentYearInstant_NonConsolidatedMember"
                currentDuration = "CurrentYearDuration_NonConsolidatedMember"
            elif TypeOfCurrentPeriodDEI == "HY":
                currentInstant = "InterimInstant_NonConsolidatedMember"
                currentDuration = "InterimDuration_NonConsolidatedMember"
            elif TypeOfCurrentPeriodDEI == "Q1" or "Q2" or "Q3" or "Q4" or "Q5":
                currentInstant = "CurrentQuarterInstant_NonConsolidatedMember"
                currentDuration = "CurrentYTDDuration_NonConsolidatedMember"
        else:
            print("連結、個別共に財務諸表がありません")
        contextIDDict = {"currentInstant":currentInstant,"currentDuration":currentDuration,"FilingDateInstant":"FilingDateInstant"}
        return contextIDDict
    
    def parseXBRL_DEI(self,xbrlFilePath) -> dict:
        coreData_dict = CoreData().to_dict()
        keys = coreData_dict.keys()
        cntrl = Cntlr.Cntlr(logFileName='logToPrint')
        model_xbrl = cntrl.modelManager.load(xbrlFilePath)
        coreData_dict = {}
        for fact in model_xbrl.facts:
            if fact.contextID == "FilingDateInstant" and fact.concept.name in keys:
                coreData_dict[fact.concept.name] = fact.value
        return coreData_dict
    

    def pickUpAccountValue(self,xbrl_file_path:str,coreData_dict:dict) -> list:
        if coreData_dict.get("AccountingStandardsDEI") == AccountingStandardClass.ifrs.value:
            return self.pickUpAccountValue_IFRS(xbrl_file_path,coreData_dict)
        elif coreData_dict.get("AccountingStandardsDEI") == AccountingStandardClass.us_gaap.value:
            return self.pickUpAccountValue_USGAAP(xbrl_file_path,coreData_dict)
        else:
            return self.pickUpAccountValue_JapanGAAP(xbrl_file_path,coreData_dict)

    def priorToPickUpAccountValue_JapanGAAP_private(self,coreData_dict:dict) -> dict:
        industryCode:IndustryCode = None
        bsdict = BS_Tag.dict()
        pldict = PL_Tag.dict()
        if coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"] == "true":
            industryCode = str(coreData_dict["IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
        else:
            industryCode = str(coreData_dict["IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()

        if industryCode == IndustryCode.BNK.value:
            pldict = PL_Tag_BNK.dict()
        elif industryCode == IndustryCode.SEC.value:
            pldict = PL_Tag_SEC.dict()
        elif industryCode == IndustryCode.INS.value:
            pldict = PL_Tag_INS.dict()
        else:
            pass
        return {"bs":bsdict,"pl":pldict}

    def pickUpAccountValue_JapanGAAP(self,xbrl_file_path,coreData_dict) -> list:
        cntrl = Cntlr.Cntlr(logFileName='logToPrint')
        model_xbrl = cntrl.modelManager.load(xbrl_file_path)
        contextID_dict = self.makeContextIDDict(coreData_dict["TypeOfCurrentPeriodDEI"],coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"])
        fs_dict = self.priorToPickUpAccountValue_JapanGAAP_private(coreData_dict)
        all_dict_list = []
        all_dict_list.append(coreData_dict)
        dict_bs:dict = fs_dict["bs"]
        dict_pl:dict = fs_dict["pl"]
        dict_cf = CF_Tag.dict()
        dict_other = OtherData_Tag.dict()
        dict_bs_keys = dict_bs.keys()
        dict_pl_keys = dict_pl.keys()
        dict_cf_keys = dict_cf.keys()
        dict_bs_keys = dict_bs.keys()
        contextID_values = contextID_dict.values()
        for fact in model_xbrl.facts:
            if fact.concept.name in dict_bs_keys and fact.contextID == contextID_dict["currentInstant"] and fact.value != '':
                dict_bs[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_pl_keys and fact.contextID == contextID_dict["currentDuration"] and fact.value != '':
                dict_pl[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_cf_keys and fact.contextID in contextID_values and fact.value != '':
                dict_cf[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.NumberOfIssuedSharesAsOfFiscalYearEndIssuedSharesTotalNumberOfSharesEtc.value and fact.contextID == "FilingDateInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.TotalNumberOfSharesHeldTreasurySharesEtc.value and fact.contextID == "CurrentYearInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
        dict_pl = self.afterPickUpAccountValue_JapanGAAP_private(coreData_dict,dict_pl)
        all_dict_list.append(dict_bs)
        all_dict_list.append(dict_pl)
        all_dict_list.append(dict_cf)
        all_dict_list.append(dict_other)
        return all_dict_list

    def afterPickUpAccountValue_JapanGAAP_private(self,coreData_dict,pl_dict:dict) -> dict:
        industryCode:IndustryCode = None
        pldict = pl_dict
        # 連結非連結ごとの処理
        if coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"] == "true":
            industryCode = str(coreData_dict["IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
        else:
            industryCode = str(coreData_dict["IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
        
        ## 業種ごとの処理
        if industryCode != IndustryCode.INS.value and industryCode != IndustryCode.BNK.value and industryCode != IndustryCode.SEC.value:
            if pl_dict.get(PL_Tag.NetSales.value) and pl_dict.get(PL_Tag.OperatingRevenue1.value):
                pldict.pop(PL_Tag.NetSales.value)
            elif pl_dict.get(PL_Tag.NetSales.value):
                pldict.pop(PL_Tag.OperatingRevenue1.value)
            elif pldict.get(PL_Tag.OperatingRevenue1.value):
                pldict.pop(PL_Tag.NetSales.value)
        else:
            pass
        return pldict
    
    def pickUpAccountValue_IFRS(self,xbrl_file_path,coreData_dict) -> list:
        cntrl = Cntlr.Cntlr(logFileName='logToPrint')
        model_xbrl = cntrl.modelManager.load(xbrl_file_path)
        contextID_dict = self.makeContextIDDict(coreData_dict["TypeOfCurrentPeriodDEI"],coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"])
        all_dict_list = []
        all_dict_list.append(coreData_dict)
        dict_bs = BS_Tag_IFRS.dict()
        dict_pl = PL_Tag_IFRS.dict()
        dict_cf = CF_Tag_IFRS.dict()
        dict_other = OtherData_Tag.dict()
        dict_bs_keys = dict_bs.keys()
        dict_pl_keys = dict_pl.keys()
        dict_cf_keys = dict_cf.keys()
        dict_bs_keys = dict_bs.keys()
        contextID_values = contextID_dict.values()
        for fact in model_xbrl.facts:
            if fact.concept.name in dict_bs_keys and fact.contextID == contextID_dict["currentInstant"] and fact.value != '':
                dict_bs[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_pl_keys and fact.contextID == contextID_dict["currentDuration"] and fact.value != '':
                dict_pl[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_cf_keys and fact.contextID in contextID_values and fact.value != '':
                dict_cf[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.NumberOfIssuedSharesAsOfFiscalYearEndIssuedSharesTotalNumberOfSharesEtc.value and fact.contextID == "FilingDateInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.TotalNumberOfSharesHeldTreasurySharesEtc.value and fact.contextID == "CurrentYearInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
        ifrs_revenue_list = [dict_pl[PL_Tag_IFRS.RevenueIFRS.value],dict_pl[PL_Tag_IFRS.NetSalesIFRS.value],dict_pl[PL_Tag_IFRS.Revenue2IFRS.value]]
        if ifrs_revenue_list.count(None) == 3:
            print(F"{coreData_dict['FilerNameInJapaneseDEI']}:IFRS売上でエラー発生")
        else:
            value = max(v for v in ifrs_revenue_list if v is not None)
            key = [k for k,v in dict_pl.items() if v == value][0]
            if key == PL_Tag_IFRS.RevenueIFRS.value:
                dict_pl.pop(PL_Tag_IFRS.NetSalesIFRS.value)
                dict_pl.pop(PL_Tag_IFRS.Revenue2IFRS.value)
            elif key == PL_Tag_IFRS.Revenue2IFRS.value:
                dict_pl.pop(PL_Tag_IFRS.NetSalesIFRS.value)
                dict_pl.pop(PL_Tag_IFRS.RevenueIFRS.value)
            elif key == PL_Tag_IFRS.NetSalesIFRS.value:
                dict_pl.pop(PL_Tag_IFRS.Revenue2IFRS.value)
                dict_pl.pop(PL_Tag_IFRS.RevenueIFRS.value)   
        if dict_bs['AssetsIFRS'] == None:
            return self.pickUpAccountValue_IFRS_Simple(xbrl_file_path,coreData_dict)
        all_dict_list.append(dict_bs)
        all_dict_list.append(dict_pl)
        all_dict_list.append(dict_cf)
        all_dict_list.append(dict_other)
        return all_dict_list
    
    def pickUpAccountValue_USGAAP(self,xbrl_file_path,coreData_dict) ->list:
        cntrl = Cntlr.Cntlr(logFileName='logToPrint')
        model_xbrl = cntrl.modelManager.load(xbrl_file_path)
        contextID_dict = self.makeContextIDDict(coreData_dict["TypeOfCurrentPeriodDEI"],coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"])
        all_dict_list = []
        all_dict_list.append(coreData_dict)
        dict_bs = USGAAP_BS_Tag.dict()
        dict_pl = USGAAP_PL_Tag.dict()
        dict_cf = USGAAP_CF_Tag.dict()
        dict_other = OtherData_Tag.dict()
        dict_bs_keys = dict_bs.keys()
        dict_pl_keys = dict_pl.keys()
        dict_cf_keys = dict_cf.keys()
        dict_bs_keys = dict_bs.keys()
        contextID_values = contextID_dict.values()
        for fact in model_xbrl.facts:
            if fact.concept.name in dict_bs_keys and fact.contextID == contextID_dict["currentInstant"] and fact.value != '':
                dict_bs[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_pl_keys and fact.contextID == contextID_dict["currentDuration"] and fact.value != '':
                dict_pl[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_cf_keys and fact.contextID in contextID_values and fact.value != '':
                dict_cf[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.NumberOfIssuedSharesAsOfFiscalYearEndIssuedSharesTotalNumberOfSharesEtc.value and fact.contextID == "FilingDateInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.TotalNumberOfSharesHeldTreasurySharesEtc.value and fact.contextID == "CurrentYearInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
        
        all_dict_list.append(dict_bs)
        all_dict_list.append(dict_pl)
        all_dict_list.append(dict_cf)
        all_dict_list.append(dict_other)
        return all_dict_list
    
    def pickUpAccountValue_IFRS_Simple(self,xbrl_file_path,coreData_dict) ->list:
        cntrl = Cntlr.Cntlr(logFileName='logToPrint')
        model_xbrl = cntrl.modelManager.load(xbrl_file_path)
        contextID_dict = self.makeContextIDDict(coreData_dict["TypeOfCurrentPeriodDEI"],coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"])
        all_dict_list = []
        all_dict_list.append(coreData_dict)

        dict_bs = IFRS_Simple_BS_Tag.dict()
        dict_pl = IFRS_Simple_PL_Tag.dict()
        dict_cf = IFRS_Simple_CF_Tag.dict()
        
        dict_other = OtherData_Tag.dict()
        

        dict_bs_keys = dict_bs.keys()
        dict_pl_keys = dict_pl.keys()
        dict_cf_keys = dict_cf.keys()
        dict_bs_keys = dict_bs.keys()
        contextID_values = contextID_dict.values()
        for fact in model_xbrl.facts:
            if fact.concept.name in dict_bs_keys and fact.contextID == contextID_dict["currentInstant"] and fact.value != '':
                dict_bs[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_pl_keys and fact.contextID == contextID_dict["currentDuration"] and fact.value != '':
                dict_pl[fact.concept.name] = int(fact.value)
            elif fact.concept.name in dict_cf_keys and fact.contextID in contextID_values and fact.value != '':
                dict_cf[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.NumberOfIssuedSharesAsOfFiscalYearEndIssuedSharesTotalNumberOfSharesEtc.value and fact.contextID == "FilingDateInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
            elif fact.concept.name == OtherData_Tag.TotalNumberOfSharesHeldTreasurySharesEtc.value and fact.contextID == "CurrentYearInstant" and fact.value != '':
                dict_other[fact.concept.name] = int(fact.value)
        ## ここでタグを切り替える
        dict_bs = From_SimpleIFRS_to_IFRS.BS_from_SimpleIFRS_to_IFRS(dict_bs)
        dict_pl = From_SimpleIFRS_to_IFRS.PL_from_SimpleIFRS_to_IFRS(dict_pl)
        dict_cf = From_SimpleIFRS_to_IFRS.CF_from_SimpleIFRS_to_IFRS(dict_cf)
        ##
        ifrs_revenue_list = [dict_pl[PL_Tag_IFRS.RevenueIFRS.value],dict_pl[PL_Tag_IFRS.NetSalesIFRS.value],dict_pl[PL_Tag_IFRS.Revenue2IFRS.value]]
        if ifrs_revenue_list.count(None) == 3:
            print(F"{coreData_dict['FilerNameInJapaneseDEI']}:IFRS売上でエラー発生")
        else:
            value = max(v for v in ifrs_revenue_list if v is not None)
            key = [k for k,v in dict_pl.items() if v == value][0]
            if key == PL_Tag_IFRS.RevenueIFRS.value:
                dict_pl.pop(PL_Tag_IFRS.NetSalesIFRS.value)
                dict_pl.pop(PL_Tag_IFRS.Revenue2IFRS.value)
            elif key == PL_Tag_IFRS.Revenue2IFRS.value:
                dict_pl.pop(PL_Tag_IFRS.NetSalesIFRS.value)
                dict_pl.pop(PL_Tag_IFRS.RevenueIFRS.value)
            elif key == PL_Tag_IFRS.NetSalesIFRS.value:
                dict_pl.pop(PL_Tag_IFRS.Revenue2IFRS.value)
                dict_pl.pop(PL_Tag_IFRS.RevenueIFRS.value)   
        

        all_dict_list.append(dict_bs)
        all_dict_list.append(dict_pl)
        all_dict_list.append(dict_cf)
        all_dict_list.append(dict_other)
        return all_dict_list




class SaveDataClass():
    def encodeDate(self,date_str) -> datetime.datetime:
        tdatetime = datetime.datetime.strptime(date_str,'%Y-%m-%d')
        tdate = datetime.datetime(tdatetime.year,tdatetime.month,tdatetime.day)
        return tdate
    def saveCorporateCoreData(self,coreData_dict:dict):
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]])#Company
        jpName = str(coreData_dict["FilerNameInJapaneseDEI"]).replace(" ","")#半角スペースなくす
        jpName = jpName.replace("　","")#全角スペースなくす
        jpName = jpName.replace("株式会社","")#「株式会社」なくす
        secCode = ""
        if coreData_dict["SecurityCodeDEI"] != "":
            secCode = str(int(int(coreData_dict["SecurityCodeDEI"]) / 10))
        jcn:str = jcn_str_dict[coreData_dict["EDINETCodeDEI"]]
        search_companyName_dict[jcn] = jpName
        search_secCode_dict[jcn] = secCode
        doc_ref.set({
            u'JCN':jcn_str_dict[coreData_dict["EDINETCodeDEI"]],
            u'EDINETCode':coreData_dict["EDINETCodeDEI"],
            u'CorporateJPNName':coreData_dict["FilerNameInJapaneseDEI"],
            u'CorporateENGName':coreData_dict["FilerNameInEnglishDEI"],
            u'SecCode':coreData_dict["SecurityCodeDEI"],
            u'lastModified':datetime.datetime.now(tz=datetime.timezone.utc),
            u'jpName':jpName,
            u'SecCode_search':secCode
        })
    def saveCorporateFinancialData(self,docID:str,all_list:dict):
        coreData_dict = all_list[0]
        bs_dict = all_list[1]
        pl_dict = all_list[2]
        cf_dict = all_list[3]
        other_dict = all_list[4]
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]]).collection(u'FinDocument').document(docID)
        industry_code = ""
        if coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"] == "true":
            industry_code = str(coreData_dict["IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
        else:
            industry_code = str(coreData_dict["IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
        doc_ref.set({
            u'FiscalYear':coreData_dict["FiscalYearCoverPage"],
            u'AccountingStandard':coreData_dict["AccountingStandardsDEI"],
            u'ordinanceCode':u'010',
            u'formCode':u'030000',
            u'IndustryCodeDEI':industry_code,
            u'WhetherConsolidated':coreData_dict["WhetherConsolidatedFinancialStatementsArePreparedDEI"],
            u'CurrentFiscalYearStartDate':self.encodeDate(coreData_dict["CurrentFiscalYearStartDateDEI"]),
            u'CurrentPeriodEndDate':self.encodeDate(coreData_dict["CurrentPeriodEndDateDEI"]),
            u'CurrentFiscalYearEndDate':self.encodeDate(coreData_dict["CurrentFiscalYearEndDateDEI"]),
            u'TypeOfCurrentPeriod':coreData_dict["TypeOfCurrentPeriodDEI"]
        })
        self.saveCorporationBSCoreData(docID,bs_dict,coreData_dict)
        self.saveCorporationPLCoreData(docID,pl_dict,coreData_dict)
        self.saveCorporationCFCoreData(docID,cf_dict,coreData_dict)
        self.saveCorporationOtherData(docID,other_dict,coreData_dict)
        self.saveCorporationFinIndexData(docID,bs_dict,pl_dict,cf_dict,coreData_dict)
    def saveCorporationBSCoreData(self,docID,bsdict:dict,coreData_dict:dict):
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]]).collection(u'FinDocument').document(docID).collection(u'DetailData').document(u'BSCoreData')
        doc_ref.set(bsdict)
    def saveCorporationPLCoreData(self,docID,pldict:dict,coreData_dict:dict):
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]]).collection(u'FinDocument').document(docID).collection(u'DetailData').document(u'PLCoreData')
        keys = list(pldict.keys())
        doc_ref.set(pldict)
    def saveCorporationCFCoreData(self,docID,cfdict:dict,coreData_dict:dict):
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]]).collection(u'FinDocument').document(docID).collection(u'DetailData').document(u'CFCoreData')
        keys = list(cfdict.keys())
        doc_ref.set(cfdict)
    def saveCorporationOtherData(self,docID,otherdict:dict,coreData_dict:dict):
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]]).collection(u'FinDocument').document(docID).collection(u'DetailData').document(u'OtherData')
        doc_ref.set(otherdict)
    def saveCorporationFinIndexData(self,docID,bs,pl,cf,coreData_dict:dict):
        doc_ref = db.collection(u'COMPANY').document(jcn_str_dict[coreData_dict["EDINETCodeDEI"]]).collection(u'FinDocument').document(docID).collection(u'DetailData').document(u'FinIndex')
        finIndexdict = self.calFinIndex(bs,pl,cf,coreData_dict)
        doc_ref.set(finIndexdict.to_dict())
    def calFinIndex(self,bs:dict,pl:dict,cf:dict,core:dict) -> FinIndex:
        finIndex = FinIndex()
        if core["AccountingStandardsDEI"] == AccountingStandardClass.ifrs.value:
            NetSales = None
            if pl.get(PL_Tag_IFRS.RevenueIFRS.value) != None:
                NetSales = pl[PL_Tag_IFRS.RevenueIFRS.value]
            elif pl.get(PL_Tag_IFRS.Revenue2IFRS.value) != None:
                NetSales = pl[PL_Tag_IFRS.Revenue2IFRS.value]
            elif pl.get(PL_Tag_IFRS.NetSalesIFRS.value) != None:
                NetSales = pl[PL_Tag_IFRS.NetSalesIFRS.value]

            try:
                finIndex.ECR = bs[BS_Tag_IFRS.EquityAttributableToOwnersOfParentIFRS.value] / bs[BS_Tag_IFRS.AssetsIFRS.value]
            except:
                pass
            try:
                finIndex.CR = bs[BS_Tag_IFRS.CurrentAssetsIFRS.value] / bs[BS_Tag_IFRS.TotalCurrentLiabilitiesIFRS.value]
            except:
                pass
            try:
                finIndex.FAR = bs[BS_Tag_IFRS.NonCurrentAssetsIFRS.value] / bs[BS_Tag_IFRS.EquityAttributableToOwnersOfParentIFRS.value]
            except:
                pass
            try:
                finIndex.FAR2 = bs[BS_Tag_IFRS.NonCurrentAssetsIFRS.value] / (bs[BS_Tag_IFRS.EquityAttributableToOwnersOfParentIFRS.value] + bs[BS_Tag_IFRS.NonCurrentLiabilitiesIFRS.value])
            except:
                pass
            try:
                finIndex.OMR = pl[PL_Tag_IFRS.OperatingProfitLossIFRS.value] / NetSales
            except:
                pass
            try:
                finIndex.NPMR = pl[PL_Tag_IFRS.ProfitLossAttributableToOwnersOfParentIFRS.value] / NetSales 
            except:
                pass
            try:
                finIndex.売上営業CF比率 = cf[CF_Tag_IFRS.NetCashProvidedByUsedInOperatingActivitiesIFRS.value] / NetSales
            except:
                pass
            try:
                finIndex.自己資本営業CF比率 = cf[CF_Tag_IFRS.NetCashProvidedByUsedInOperatingActivitiesIFRS.value] / bs[BS_Tag_IFRS.EquityAttributableToOwnersOfParentIFRS.value]
            except:
                pass
            try:
                finIndex.CFATR = cf[CF_Tag_IFRS.NetCashProvidedByUsedInOperatingActivitiesIFRS.value] / bs[BS_Tag_IFRS.TotalCurrentLiabilitiesIFRS.value]
            except:
                pass
            try:
                finIndex.ROA = pl[PL_Tag_IFRS.ProfitLossAttributableToOwnersOfParentIFRS.value] / bs[BS_Tag_IFRS.AssetsIFRS.value]
            except:
                pass
            try:
                finIndex.ROE = pl[PL_Tag_IFRS.ProfitLossAttributableToOwnersOfParentIFRS.value] / bs[BS_Tag_IFRS.EquityAttributableToOwnersOfParentIFRS.value]
            except:
                pass

        elif core["AccountingStandardsDEI"] == AccountingStandardClass.us_gaap.value:
            OwnerAssets = bs[USGAAP_BS_Tag.EquityAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults.value]
            Assets = bs[USGAAP_BS_Tag.TotalAssetsUSGAAPSummaryOfBusinessResults.value]
            NetSales = pl[USGAAP_PL_Tag.RevenuesUSGAAPSummaryOfBusinessResults.value]
            OperatingIncome = pl[USGAAP_PL_Tag.OperatingIncomeLossUSGAAPSummaryOfBusinessResults.value]
            ParentIncome = pl[USGAAP_PL_Tag.NetIncomeLossAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults.value]
            try:
                finIndex.ECR = OwnerAssets / Assets
            except:
                pass
            try:
                finIndex.OMR = OperatingIncome / NetSales
            except:
                pass
            try:
                finIndex.NPMR = ParentIncome / NetSales
            except:
                pass
            try:
                finIndex.売上営業CF比率 = cf[USGAAP_CF_Tag.CashFlowsFromUsedInOperatingActivitiesUSGAAPSummaryOfBusinessResults.value] / NetSales
            except:
                pass
            try:
                finIndex.自己資本営業CF比率 = cf[USGAAP_CF_Tag.CashFlowsFromUsedInOperatingActivitiesUSGAAPSummaryOfBusinessResults.value] / OwnerAssets
            except:
                pass
            try:
                finIndex.ROA = ParentIncome / Assets
            except:
                pass
            try:
                finIndex.ROE = ParentIncome / OwnerAssets
            except:
                pass
        else:
            industryCode:IndustryCode = None
            if core["WhetherConsolidatedFinancialStatementsArePreparedDEI"] == "true":
                industryCode = str(core["IndustryCodeWhenConsolidatedFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
            else:
                industryCode = str(core["IndustryCodeWhenFinancialStatementsArePreparedInAccordanceWithIndustrySpecificRegulationsDEI"]).upper()
            NetSalesJP = None

            if industryCode == IndustryCode.INS.value:
                NetSales = PL_Tag_INS.OperatingIncomeINS
            elif industryCode == IndustryCode.BNK.value:
                NetSales = PL_Tag_BNK.OrdinaryIncomeBNK
            elif industryCode == IndustryCode.SEC.value:
                NetSales = PL_Tag_SEC.OperatingRevenueSEC
            elif pl.get(PL_Tag.OperatingRevenue1.value) != None:
                NetSalesJP = pl[PL_Tag.OperatingRevenue1.value]
            elif pl.get(PL_Tag.NetSales.value) != None:
                NetSalesJP = pl[PL_Tag.NetSales.value]
            
            OwnerAssets = bs.get(BS_Tag.NetAssets.value)
            try:
                OwnerAssets = bs[BS_Tag.NetAssets.value] - bs[BS_Tag.NonControllingInterests.value]
            except:
                pass
            try:
                finIndex.ECR = OwnerAssets / bs[BS_Tag.Assets.value]
            except:
                pass
            try:
                finIndex.CR = bs[BS_Tag.CurrentAssets.value] / bs[BS_Tag.CurrentLiabilities.value]
            except:
                pass
            try:
                finIndex.FAR = bs[BS_Tag.NoncurrentAssets.value] / OwnerAssets
            except:
                pass
            try:
                finIndex.FAR2 = bs[BS_Tag.NoncurrentAssets.value] / (OwnerAssets + bs[BS_Tag.NoncurrentLiabilities.value])
            except:
                pass
            try:
                finIndex.OMR = pl[PL_Tag.OperatingIncome.value] / NetSalesJP
            except:
                pass
            try:
                finIndex.NPMR = pl[PL_Tag.ProfitLossAttributableToOwnersOfParent.value] / NetSalesJP
            except:
                pass
            try:
                finIndex.売上営業CF比率 = cf[CF_Tag.NetCashProvidedByUsedInOperatingActivities.value] / NetSalesJP
            except:
                pass
            try:
                finIndex.自己資本営業CF比率 = cf[CF_Tag.NetCashProvidedByUsedInOperatingActivities.value] / OwnerAssets
            except:
                pass
            try:
                finIndex.CFATR = cf[CF_Tag.NetCashProvidedByUsedInOperatingActivities.value] / bs[BS_Tag.CurrentLiabilities.value]
            except:
                pass
            try:
                finIndex.ROA = pl[PL_Tag.ProfitLossAttributableToOwnersOfParent.value] / bs[BS_Tag.Assets.value]
            except:
                pass
            try:
                finIndex.ROE = pl[PL_Tag.ProfitLossAttributableToOwnersOfParent.value] / OwnerAssets
            except:
                pass




        return finIndex

    def save_search_tag(self):
        doc_ref = db.collection(u'Search').document(u'JPName')
        doc_ref.set(search_companyName_dict,merge=True)
        doc_ref_1 = db.collection(u'Search').document(u'SecCode')
        doc_ref_1.set(search_secCode_dict,merge=True)
        
        

        


        

def 保存するtoCsvFile(jcn_dict:dict):
    for i in range(len(all_dict_list)):
        dic:dict =  all_dict_list[i]
        dic_keys = dic.keys()
        dic_value = dic.values()
        with open(F"D:XBRL_Download//{EDINETCodeDEI}{i}.csv","w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(dic_keys)
            writer.writerow(dic_value)
    
core30List = ["72030","67580","99840","68610","83060","60980","79740","40630","94320","65940","45020","65010","77410","72670","94330","63670","83160","69810","69540","80010","84110","33820","80310","45680","80580","45030","87660","44520","90220"]
nikkei225 = [6472,3103,7211,9501,7003,5020,7186,4902,7762,5202,8308,8604,1332,5406,4005,4689,7201,3861,5803,3289,3402,8601,6471,8306,8331,7004,1803,8628,8355,3099,7261,4188,6703,1802,4755,6473,6178,7752,7205,3405,3086,8233,9503,3407,1963,6113,2531,1605,3863,9502,8002,4506,5301,7731,6752,6753,3101,8253,6770,1812,4751,7202,3401,1808,9434,5411,6503,6952,5802,9005,8411,2002,8802,5101,8795,8804,5703,8053,4042,6724,2432,2768,4043,5333,2503,5401,4503,6841,9532,5711,9007,4208,7270,8252,3436,7911,8303,7012,2501,9613,8354,7203,3659,9531,5233,1928,7013,2914,5707,8697,5801,8801,4004,6326,9202,1333,6674,4568,9064,7733,8750,5541,8267,2871,8304,7272,9001,7912,1721,7751,6301,9301,5214,8031,6479,4151,6302,4631,5019,4183,6305,7011,9009,2802,5706,9432,1925,7267,4502,8830,5232,9433,8001,4519,5631,1801,8058,8725,4578,8309,4061,4324,8316,4543,2282,2413,9602,6762,8015,2502,6103,5332,7269,6506,9021,5714,6701,5108,9984,9008,5201,7951,5713,8630,6361,6098,6976,4452,4523,3382,6501,4911,6504,4704,4021,9766,9147,6971,8766,9020,4507,2269,9107,4901,7832,9735,2801,6645,6902,6988,6981,9104,9101,6857,7735,6758,6702,9022,4063,6954,6367,8035,7974,6861,9983]#
SearchSecCode = [1332,1333,1414,1417,1605,1721,1801,1802,1803,1808,1812,1820,1860,1878,1893,1911,1925,1928,1944,1951,1959,1963,2002,2127,2175,2181,2201,2206,2212,2229,2264,2267,2269,2270,2282,2331,2371,2412,2413,2427,2432,2433,2492,2501,2502,2503,2531,2579,2587,2593,2607,2651,2670,2768,2784,2801,2802,2809,2810,2811,2815,2871,2875,2897,2914,3003,3038,3064,3086,3088,3092,3099,3101,3105,3107,3116,3141,3197,3231,3288,3289,3291,3349,3360,3382,3391,3401,3402,3405,3407,3436,3549,3563,3591,3626,3635,3659,3697,3765,3769,3774,3861,3863,3880,3923,3941,3994,4004,4005,4021,4042,4043,4045,4061,4062,4063,4088,4091,4114,4118,4151,4182,4183,4185,4186,4188,4202,4203,4204,4205,4206,4208,4272,4307,4324,4401,4403,4443,4452,4502,4503,4506,4507,4516,4519,4521,4523,4527,4528,4530,4534,4536,4540,4543,4544,4552,4568,4578,4581,4587,4612,4613,4631,4661,4665,4666,4676,4681,4684,4686,4689,4704,4716,4732,4739,4751,4755,4768,4887,4901,4902,4911,4912,4919,4921,4922,4927,4967,5019,5020,5021,5076,5101,5105,5108,5110,5201,5214,5232,5233,5301,5332,5333,5334,5401,5406,5411,5444,5463,5471,5486,5631,5703,5706,5711,5713,5714,5801,5802,5901,5929,5938,5947,5991,6005,6028,6098,6103,6113,6134,6136,6141,6146,6178,6201,6268,6273,6301,6302,6305,6326,6361,6367,6370,6383,6395,6406,6417,6436,6448,6457,6460,6465,6471,6472,6473,6479,6481,6501,6502,6503,6504,6506,6532,6586,6592,6594,6645,6674,6701,6702,6723,6724,6728,6752,6753,6754,6755,6758,6762,6770,6806,6841,6845,6849,6856,6857,6861,6869,6902,6920,6923,6925,6951,6952,6954,6963,6965,6967,6971,6976,6981,6988,7011,7012,7013,7164,7167,7180,7181,7182,7186,7201,7202,7203,7205,7211,7240,7259,7261,7267,7269,7270,7272,7276,7282,7309,7313,7337,7453,7458,7459,7476,7518,7532,7550,7616,7649,7701,7730,7731,7732,7733,7735,7741,7747,7751,7752,7780,7832,7846,7911,7912,7936,7947,7951,7956,7966,7974,7984,7988,8001,8002,8012,8015,8031,8035,8053,8056,8058,8060,8086,8088,8111,8113,8129,8136,8227,8233,8252,8253,8267,8273,8279,8282,8283,8303,8304,8306,8308,8309,8316,8331,8334,8354,8355,8359,8369,8377,8382,8385,8410,8411,8418,8439,8473,8570,8572,8591,8593,8595,8601,8604,8630,8697,8725,8750,8766,8795,8801,8802,8804,8830,8876,8905,9001,9003,9005,9006,9007,9008,9009,9020,9021,9022,9024,9031,9041,9042,9044,9045,9048,9064,9065,9072,9076,9086,9101,9104,9107,9142,9143,9147,9201,9202,9301,9364,9401,9404,9409,9432,9433,9434,9435,9449,9468,9501,9502,9503,9504,9505,9506,9507,9508,9509,9513,9531,9532,9533,9601,9602,9613,9627,9684,9697,9706,9719,9735,9744,9766,9783,9831,9832,9843,9861,9962,9983,9984,9987,9989]
SearchSecCode_encode = []
for i in SearchSecCode:
    i = i * 10
    SearchSecCode_encode.append(F"{i}")

if __name__ == "__main__":
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    start = time.time()
    fetch_xbrl_file = FetchXBRLFileClass()
    parse_xbrl_file = ParseXBRLFileClass()
    save_data = SaveDataClass()

    ## ここでmodeを切り替える
    ### 0 : 内部データから取得
    ### 1 : APIを利用して特定の期間のデータをダウンロードして取得
    mode = 0
    ##
    
    folder_name_list = []

    
    print(folder_name_list)

    #xbrl_file_paths = ["C://Users//taku3//OneDrive//デスクトップ//XBRL_test//PublicDoc//jpcrp030000-asr-001_E03061-000_2021-02-28_01_2021-05-27.xbrl"] #テスト用

    xbrl_files_path_parent = "D:XBRL_Download//"
    xbrl_files_path_child = "//XBRL//PublicDoc//*.xbrl"

    for i in range(len(folder_name_list)):
        folder_name = folder_name_list[i]
        xbrl_files_path = glob.glob(f'{xbrl_files_path_parent}{folder_name}{xbrl_files_path_child}')
        fainalIndex = len(folder_name_list) - 1
        for j in range(len(xbrl_files_path)):
            file = xbrl_files_path[j]
            #jcn_str_dict["E03061"] = "000"#テスト用
            #docID_str_list.append("TESTID")#テスト用
            dict_dei:dict = parse_xbrl_file.parseXBRL_DEI(file)
            if dict_dei == {}:
                pass
            else:
                
                all_dict_list = parse_xbrl_file.pickUpAccountValue(file,dict_dei)
                save_data.saveCorporateCoreData(dict_dei)
                save_data.saveCorporateFinancialData(folder_name,all_dict_list)

        shutil.rmtree(F'{xbrl_files_path_parent}{folder_name}')
        print(f'{i} / {fainalIndex}')
    save_data.save_search_tag()
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    #shutil.rmtree('D:XBRL_Download//XBRL//')
    print("終了しました")
