from datetime import date
import datetime
import re
import time
from urllib.request import Request
from arelle import Cntlr
from arelle import ModelXbrl
import sys
from EDINETLoader import FetchXBRLFileClass
import requests
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
from bs4 import Tag
import re
import glob
import os
import shutil

class parseTDnet:

    def __init__(self,sleepTime=1) -> None:
        self.sleeptime = sleepTime
        self.baseUrl = "https://www.release.tdnet.info/inbs/"
    def parse(self,datelist:list[date]=None,download_dir="G:Parse_Xbrl_of_TDnet//"):
        datelist = datelist
        if datelist == None:
            e_date = datetime.date.today()
            s_date = e_date - relativedelta(days=40)
            datelist = FetchXBRLFileClass().makeDayList_private(s_date,e_date)
        for d in datelist:
            date = d.strftime('%Y%m%d')
            search_args = f"I_list_001_{date}.html"
            self.parserTDnetHTML(search_args,download_dir)
        self.unzip_File(download_dir)
        
                
    def parserTDnetHTML(self,args,download_dir):
        # アクセス制御
        time.sleep(self.sleeptime)
        url = self.baseUrl + args
        res:requests.Response = requests.get(url,)
        if not res.ok:
            print(url)
            print(f"{res.status_code}")
            return
        res.encoding = "utf-8"
        soup = bs(res.text, 'html.parser')
        isKaiji = soup.find(id="kaiji-text-1")
        if isKaiji.contents[0] == "に開示された情報はありません。":
            return
        # ここでXbrlのfileを探す
        fileList = self.fetchXbrlFile(soup)
        # ここでdownload
        self.download(fileList,download_dir)
        next = soup.find(class_="pager-R")
        temp = next.attrs['onclick']
        nextUrls = re.findall("I_list.+html",temp)
        if len(nextUrls) == 0:
            return
        self.parserTDnetHTML(nextUrls[0],download_dir)
    
    def fetchXbrlFile(self,soup:bs) -> list[str]:
        xbrl_buttons = soup.find_all(class_="xbrl-button")
        results = []
        for xbrl_button in xbrl_buttons:
            xbrl_button:Tag = xbrl_button
            next = xbrl_button.find("a")
            url = next.get("href")
            results.append(url)
        print(results)
        return results


    def download(self,docList:list,download_dir):
        '''docListのXBRLをダウンロードする'''
        files = os.listdir(download_dir)
        downloadedFiles = [f for f in files if os.path.isdir(os.path.join(download_dir, f))]
        docList_remove_zip = [f.replace(".zip","") for f in docList]
        docList = list(set(docList_remove_zip) - set(downloadedFiles))
        docList = [f + ".zip" for f in docList]
        finish_count = len(docList)
        print(f"ダウンロードするファイル数 : {finish_count}")
        for index, docName in enumerate(docList):
            # アクセス制御
            time.sleep(self.sleeptime)
            url = self.baseUrl + docName
            filename = download_dir + docName
            res = requests.get(url)
            if res.ok:
                with open(filename,"wb") as file:
                    for chunk in res.iter_content(chunk_size=1024):
                        file.write(chunk)       
            else:
                print("失敗しました")
                print(res.status_code)
            print(f"download : {index + 1}/{finish_count}") 
        print("ダウンロードが終了しました")

    def unzip_File(self,zipDir) -> list:
        '''zipFileを展開しxbrlFileを取り出す'''
        folders = []
        zip_Files = glob.glob(os.path.join(zipDir,'*.zip'))
        noneFile = []
        for index, zip_File in enumerate(zip_Files):
            try:
                basename_without_zip = os.path.splitext(os.path.basename(zip_File))[0]
                shutil.unpack_archive(zip_File,f'{zipDir}{basename_without_zip}')
                folders.append(basename_without_zip)
            except:
                #ファイルが壊れている
                noneFile.append(zip_File)
        print(f"展開できなかったfiles:{noneFile}")
        #不使用なzipFileを削除する
        removeZipfiles = glob.glob(zipDir + "*.zip")
        for file in removeZipfiles:
            os.remove(file)
        return folders

    def parseXBRL_of_TDnet(self,download_dir):
        #ダウンロードフォルダ内のフォルダをlist化する
        files = os.listdir(download_dir)
        dirs = [f for f in files if os.path.isdir(os.path.join(download_dir, f))]
        #フォルダの種類を調べる[Summaryがあるかどうか、Attachmentがあるかどうか]
        for dir in dirs:
            dir_childrenFiles = os.listdir(f"{download_dir}{dir}")
            dir_children_dirs = [f for f in dir_childrenFiles if os.path.isdir(os.path.join(f"{download_dir}{dir}", f))]
            if len(dir_children_dirs) == 1:
                c = os.listdir(f"{download_dir}{dir}//{dir_children_dirs[0]}")
                print(f"{dir_children_dirs}{c}")
                if len(c) < 2:
                    print(dir)
            elif len(dir_children_dirs) == 0:
                print(dir_childrenFiles)

        # 通期決算短信,四半期決算短信,業績予想の修正だけ解析して保存する

        pass



fo = open('C://Users//taku3//Downloads//2.txt', 'w', encoding='utf-8')
download_dir = "G:Parse_Xbrl_of_TDnet//"

sys.stdout = fo
import ParseXbrl
import Const
from arelle import ModelDtsObject
def tdnetXbrlParse():  
    bs = r"C:\Users\taku3\Downloads\081220220422526208\XBRLData\Attachment\0101010-acbs01-tse-acedjpfr-95010-2022-03-31-01-2022-04-28-ixbrl.html"
    summary = r"C:\Users\taku3\Downloads\081220220422526208\XBRLData\Summary\tse-acedjpsm-95010-20220422526208-ixbrl.htm"
    file_path = bs
    cntrl = Cntlr.Cntlr(logFileName='logToPrint')
    model_xbrl:ModelXbrl.ModelXbrl = cntrl.modelManager.create(url=bs,schemaRefs="G:\Parse_Xbrl_of_TDnet\081220220422526208\XBRLData\Attachment\tse-acedjpfr-95010-2022-03-31-01-2022-04-28.xsd")#(//load(file_path)
    relModels:ModelDtsObject.ModelRelationship = model_xbrl.relationshipSet(Const.presentation)
    for i,modelObject in enumerate(model_xbrl.modelObjects):
        print(modelObject)
        if type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) ==   Const.pl_root:
            ParseXbrl.printLink(Const.link_role_ConsolidatedStatementOfIncome,modelObject,0,relModels)
    '''
    facts = model_xbrl.facts
    for fact in facts:
        fact:ModelXbrl.ModelFact = fact
        try:
            print(fact.concept.qname)
        except:
            print(fact.qname)
        print(fact.value)
        '''
#parseTDnet().parseXBRL_of_TDnet(download_dir)
tdnetXbrlParse()