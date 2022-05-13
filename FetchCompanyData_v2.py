import os
import shutil
from arelle import Cntlr
import datetime
import requests
import glob
import csv
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from AccountClass import AccountingStandardClass, CoreData, DetailData, FinIndex, SaveCompanyDataToFireStore
from FetchCompanyData import FetchXBRLFileClass, ParseXBRLFileClass
from 銘柄コード import SecCodeClass as secCodes





def firebase_init():
    cred = credentials.Certificate('C://Users//taku3//Dropbox//Biz//FetchCompanyData//corporateanalysishubapp-firebase-adminsdk-n8sd4-07e702dbc7.json')
    firebase_admin.initialize_app(cred)

def secCode_enc(secCode_list) -> list:
    ls_result = []
    for secCode in secCode_list:
        ls_result.append(str(secCode * 10))
    return ls_result
if __name__ == "__main__":
    
    #################
    jcn_dict = None
    sec_dict = None
    docID_list = None
    #################
    #################
    fetch_xbrl_file = FetchXBRLFileClass()
    mode = 0
    #0 => パソコン : 1 => API
    s_date = datetime.date(2022,3,1)
    e_date = datetime.date(2022,4,10)

    seccodes = secCode_enc(secCode_list=secCodes.Mothers)
    #print(len(secCodes))
    formCode = fetch_xbrl_file.SearchParameter.formCodeType.YHO

    fetch_xbrl_file_parameter = fetch_xbrl_file.SearchParameter(mode,s_date,e_date,seccodes,formCode)
    #################
    ###ダウンロードする or フォルダ内のファイル###
    data = fetch_xbrl_file.fetchXbrlFile(parameter=fetch_xbrl_file_parameter)
    jcn_dict = data.jcn_str_dict
    sec_dict = data.secCode_str_dict
    docID_list = data.doc_id_list
    #################
    ###解析前の準備###
    xbrl_files_path_parent = "G:XBRL_For_Python_Parse//"
    xbrl_files_path_child = "//XBRL//PublicDoc//*.xbrl"
    fainalIndex = len(docID_list) - 1
    firebase_init()
    for i in range(len(docID_list)):
        folder_name = docID_list[i]
        xbrl_file_paths = glob.glob(f'{xbrl_files_path_parent}{folder_name}{xbrl_files_path_child}')
        ###解析する###
        for xbrl_file_path in xbrl_file_paths:
            ###初期化###
            cntrl = Cntlr.Cntlr(logFileName='logToPrint')
            model_xbrl = cntrl.modelManager.load(xbrl_file_path)#cntrl.modelManager.load(xbrl_file_path)
            ###coreDataの解析###
            coreData = CoreData()
            coreData.main_parse(facts=model_xbrl.facts,jcn_dict=jcn_dict,sec_dict=sec_dict)
            if coreData.EDINETCodeDEI == None:break
            ###detailDataの解析###
            detailData = DetailData()
            detailData.parse(facts=model_xbrl.facts,coreData=coreData)
            ###財務評価指数の計算###
            finIndexData = FinIndex()
            finIndexData.cal_data(core=coreData,detail=detailData)
            ###データの保存###
            db = firestore.client()
            companyCorePath = db.collection(u'COMPANY_v2').document(jcn_dict[coreData.EDINETCodeDEI])
            #htmlPath = companyCorePath.collection(u'HTML')
            finCorePath = companyCorePath.collection(u'FinDoc').document(folder_name)
            bsPath = finCorePath.collection(u'FinData').document(u'BS')
            plPath = finCorePath.collection(u'FinData').document(u'PL')
            cfPath = finCorePath.collection(u'FinData').document(u'CF')
            otherPath = finCorePath.collection(u'FinData').document(u'Other')
            finIndexPath = finCorePath.collection(u'FinData').document(u'FinIndexPath')
            #fsHTMLPath = htmlPath.document(u'FS')
            #companyHTMLPath = htmlPath.document(u'CompanyInfo')
            saveCompanyDataToFireStore = SaveCompanyDataToFireStore(companyCorePath,finCorePath,bsPath,plPath,cfPath,otherPath,"fsHTMLPath","companyHTMLPath",finIndexPath)
            saveCompanyDataToFireStore.save_company_data(coreData,detailData,finIndexData,formCode.value)
        try:
            pass
            #shutil.move(F'{xbrl_files_path_parent}{folder_name}',"D:TEMP_XBRL_Download//")
            shutil.move(F'{xbrl_files_path_parent}{folder_name}',"G:XBRL_For_Python_Did_Parse//")
        except:
            try:
                pass
                shutil.rmtree(F'{xbrl_files_path_parent}{folder_name}')
            except:pass
        print(f'{i} / {fainalIndex}')
        