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
from 銘柄コード import SecCodeClass
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
        companyName_dict = {}
        jcn_str_dict = {}
        secCode_str_dict = {}
        doc_id_list = []

        def setData(self,jcn,name,sec,docID) -> None:
            self.companyName_dict = name
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
        companyName_dict = {}
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
                        companyName_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["filerName"]
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
                        companyName_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["filerName"]
                        secCode_str_dict[jsonData["results"][num]["edinetCode"]] = jsonData["results"][num]["secCode"]
                        docID = jsonData["results"][num]["docID"]
                        docIDList.append(docID)

            
            print(f"search_doc : {index}/{finish_count}")
        print("検索が終了しました")
        result.setData(jcn=jcn_str_dict,sec=secCode_str_dict,docID=docIDList,name=companyName_dict)
        return result

    def downloadXbrlInZip_private(self,docList:list):
        '''docListのXBRLをダウンロードする'''
        print(len(docList))
        finish_count = len(docList) - 1
        for index, docID in enumerate(docList):
            time.sleep(0.1)
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
        noneFile = []
        for index, zip_File in enumerate(zip_Files):#index除かない！！
            basename_without_zip = os.path.splitext(os.path.basename(zip_File))[0]
            #with zipfile.ZipFile(zip_File) as zip_f:
            try:
                shutil.unpack_archive(zip_File,f'{zipDir}//{basename_without_zip}')
            except:
                noneFile.append(basename_without_zip)
                #self.downloadXbrlInZip_private(docList=[basename_without_zip])
                #time.sleep(10)
                #shutil.unpack_archive(zip_File,f'{zipDir}//{basename_without_zip}')
            folders.append(basename_without_zip)
                #zip_f.extractall(zipDir)
                #zip_f.close()
        #xbrl_files = glob.glob(xblrFileExpressions)
        #不使用なzipFileを削除する
        print(noneFile)
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
    
'''
def 保存するtoCsvFile(jcn_dict:dict):
    for i in range(len(all_dict_list)):
        dic:dict =  all_dict_list[i]
        dic_keys = dic.keys()
        dic_value = dic.values()
        with open(F"D:XBRL_Download//{EDINETCodeDEI}{i}.csv","w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(dic_keys)
            writer.writerow(dic_value)
'''