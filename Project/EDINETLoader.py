from cgitb import text
from datetime import datetime, timedelta
from datetime import date
import time
import requests
import glob
import os
import shutil
from enum import Enum


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
        edinetCode = {}
        doc_id_list = []

        def setData(self,jcn,name,sec,edinetCode,docID) -> None:
            self.companyName_dict = name
            self.jcn_str_dict = jcn
            self.secCode_str_dict = sec
            self.edinetCode = edinetCode
            self.doc_id_list = docID

    #ENINET API
    EDINET_API_ENDPOINT_BASE:str = "https://disclosure.edinet-fsa.go.jp/api/v1/"
    
    def edinetApiDocumentEndpoint_private(self,documentID:str) -> str:
        '''書類取得APIエンドポイント（リクエストURL）'''
        #typeは1で固定する
        edinetApiDocumentEndpoint_private = self.EDINET_API_ENDPOINT_BASE + F"documents/{documentID}?type=1"
        return edinetApiDocumentEndpoint_private
    
    def edinetApiDocumentListEndpoint_private(self,requestListDate:date,requestListResponseType:int) -> str:
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
            day = startDate + timedelta(days=i)
            dayList.append(day)
            if i == period - 1:#期間両入
                dayList.append(day + timedelta(days=1))
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
        edinetCode_dict = {}
        for index,day in enumerate(dayList):
            #time.sleep(1)
            url = self.edinetApiDocumentListEndpoint_private(day,2)
            try:
                res = requests.get(url,timeout=3.5)
            except Exception as err:
                print(err)
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
                        edinetCode_dict[jsonData["results"][num]["docID"]] = jsonData["results"][num]["edinetCode"]
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
                        edinetCode_dict[jsonData["results"][num]["docID"]] = jsonData["results"][num]["edinetCode"]
                        docID = jsonData["results"][num]["docID"]
                        docIDList.append(docID)

            
            print(f"search_doc : {index}/{finish_count}")
        print("検索が終了しました")
        result.setData(jcn=jcn_str_dict,sec=secCode_str_dict,docID=docIDList,name=companyName_dict,edinetCode=edinetCode_dict)
        return result

    def downloadXbrlInZip_private(self,docList:list):
        '''docListのXBRLをダウンロードする'''
        print(len(docList))
        finish_count = len(docList) - 1
        for index, docID in enumerate(docList):
            #time.sleep(1)
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
                folders.append(basename_without_zip)
            except:
                noneFile.append(basename_without_zip)
                #self.downloadXbrlInZip_private(docList=[basename_without_zip])
                #time.sleep(10)
                #shutil.unpack_archive(zip_File,f'{zipDir}//{basename_without_zip}')
                #zip_f.extractall(zipDir)
                #zip_f.close()
        #xbrl_files = glob.glob(xblrFileExpressions)
        #不使用なzipFileを削除する
        print(f"展開できなかったfiles:{noneFile}")
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
            e_date = date.today()
            s_date = date(year=e_date.year - 5,month=e_date.month,day=e_date.day)
        ################
        result = self.ResultData()
        path = "G:XBRL_For_Python_Parse////"
        files = os.listdir(path)
        dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
        dayList = self.makeDayList_private(s_date,e_date)
        result = self.makeDocIdList_private(dayList,parameter=parameter)
        if parameter.mode == 0:  
            result.doc_id_list = dir
            return result
        elif parameter.mode == 1:
            downloadFiles =  list(set(result.doc_id_list) - set(dir))
            self.downloadXbrlInZip_private(downloadFiles)
            self.unzip_File_private(path)
            return result
    

    def search_jcn_secCode(self,EDINETCode) -> tuple|None:
        e_date = date.today()
        s_date = date(year=e_date.year - 5,month=e_date.month,day=e_date.day)
        dayList = self.makeDayList_private(s_date,e_date)
        for i, day in enumerate(dayList):
            url = self.edinetApiDocumentListEndpoint_private(day,2)
            try:
                res = requests.get(url,timeout=3.5)
            except Exception as err:
                print(err)
            jsonData = res.json()
            if jsonData["metadata"]["status"] != "200":
                tmp = jsonData["metadata"]["status"]
                print(F"{day}:{tmp}")
                break
            else:
                for num in range(0,jsonData["metadata"]["resultset"]["count"]):
                    if jsonData["results"][num]["edinetCode"] == EDINETCode:
                        jcn = jsonData["results"][num]["JCN"]
                        secCode = jsonData["results"][num]["secCode"]
                        return (jcn, secCode)
        return None 
        

