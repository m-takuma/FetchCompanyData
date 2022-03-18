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

from AccountClass import CoreData, DetailData, FinIndex, SaveCompanyDataToFireStore
from FetchCompanyData import FetchXBRLFileClass, ParseXBRLFileClass, SaveDataClass





def firebase_init():
    cred = credentials.Certificate('C://Users//taku3//Dropbox//Biz//FetchCompanyData//corporateanalysishubapp-firebase-adminsdk-n8sd4-07e702dbc7.json')
    firebase_admin.initialize_app(cred)

def secCode_enc(secCode_list) -> list:
    ls_result = []
    for secCode in secCode_list:
        ls_result.append(str(secCode * 10))
    return ls_result
if __name__ == "__main__":
    firebase_init()
    #################
    jcn_dict = None
    sec_dict = None
    docID_list = None
    #################
    #################
    fetch_xbrl_file = FetchXBRLFileClass()
    mode = 1
    s_date = None#datetime.date(2017,1,1)
    e_date = None#datetime.date(2022,1,1)
    secCodes = secCode_enc([1332,1333,1414,1417,1605,1721,1801,1802,1803,1808,1812,1820,1860,1878,1893,1911,1944,1951,1959,1963,2002,2127,2175,2181,2201,2206,2212,2229,2264,2267,2269,2270,2282,2331,2371,2412,2427,2432,2433,2492,2501,2531,2579,2587,2593,2607,2651,2670,2768,2784,2801,2809,2810,2811,2815,2871,2875,2897,3003,3038,3064,3086,3088,3092,3099,3101,3105,3107,3116,3141,3197,3231,3288,3289,3291,3349,3360,3391,3401,3405,3436,3549,3563,3591,3626,3635,3659,3697,3765,3769,3774,3861,3863,3880,3923,3941,3994,4004,4005,4021,4042,4043,4045,4061,4062,4088,4091,4114,4118,4151,4182,4183,4185,4186,4202,4203,4204,4205,4206,4208,4272,4307,4324,4401,4403,4443,4506,4516,4521,4527,4530,4534,4536,4540,4544,4552,4581,4587,4612,4613,4631,4665,4666,4676,4681,4684,4686,4704,4716,4732,4739,4751,4755,4768,4887,4902,4912,4919,4921,4922,4927,4967,5019,5021,5076,5101,5105,5110,5201,5214,5232,5233,5301,5332,5333,5334,5406,5411,5444,5463,5471,5486,5631,5703,5706,5711,5714,5801,5901,5929,5938,5947,5991,6005,6028,6103,6113,6134,6136,6141,6146,6201,6268,6302,6305,6361,6370,6383,6395,6406,6417,6436,6448,6457,6460,6465,6471,6472,6473,6479,6481,6504,6506,6532,6592,6674,6701,6723,6724,6728,6753,6754,6755,6762,6770,6806,6841,6845,6849,6856,6857,6923,6925,6951,6952,6963,6965,6967,6976,6988,7012,7013,7164,7167,7180,7181,7182,7186,7202,7205,7211,7240,7259,7261,7272,7276,7282,7313,7337,7453,7458,7459,7476,7518,7532,7550,7616,7649,7701,7730,7731,7732,7735,7747,7752,7780,7846,7911,7912,7936,7947,7951,7956,7966,7984,7988,8012,8015,8056,8060,8086,8088,8111,8129,8136,8227,8233,8252,8253,8273,8279,8282,8283,8303,8304,8331,8334,8354,8355,8359,8369,8377,8382,8385,8410,8418,8439,8473,8570,8572,8593,8595,8795,8804,8876,8905,9001,9003,9005,9006,9007,9008,9009,9024,9031,9041,9042,9044,9045,9048,9064,9065,9072,9076,9086,9101,9104,9107,9142,9143,9147,9201,9301,9364,9401,9404,9409,9435,9449,9468,9501,9502,9503,9504,9505,9506,9507,9508,9509,9513,9531,9532,9533,9601,9602,9613,9627,9684,9697,9706,9719,9744,9766,9783,9831,9832,9861,9962,9987,9989])
    formCode = fetch_xbrl_file.SearchParameter.formCodeType.YHO
    fetch_xbrl_file_parameter = fetch_xbrl_file.SearchParameter(mode,s_date,e_date,secCodes,formCode)
    #################
    ###ダウンロードする or フォルダ内のファイル###
    data = fetch_xbrl_file.fetchXbrlFile(parameter=fetch_xbrl_file_parameter)
    jcn_dict = data.jcn_str_dict
    sec_dict = data.secCode_str_dict
    docID_list = data.doc_id_list
    #################
    ###検索用のIndex格納Dict###
    forFirestoreSearchIndexDict_name = {}
    forFirestoreSearchIndexDict_secCode = {}
    ###解析前の準備###
    xbrl_files_path_parent = "D:XBRL_Download//"
    xbrl_files_path_child = "//XBRL//PublicDoc//*.xbrl"
    fainalIndex = len(docID_list) - 1
    for i in range(len(docID_list)):
        folder_name = docID_list[i]
        xbrl_file_paths = glob.glob(f'{xbrl_files_path_parent}{folder_name}{xbrl_files_path_child}')
        ###解析する###
        for xbrl_file_path in xbrl_file_paths:
            ###初期化###
            cntrl = Cntlr.Cntlr(logFileName='logToPrint')
            model_xbrl = cntrl.modelManager.load(xbrl_file_path)
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
            htmlPath = companyCorePath.collection(u'HTML')
            finCorePath = companyCorePath.collection(u'FinDoc').document(folder_name)
            bsPath = finCorePath.collection(u'FinData').document(u'BS')
            plPath = finCorePath.collection(u'FinData').document(u'PL')
            cfPath = finCorePath.collection(u'FinData').document(u'CF')
            otherPath = finCorePath.collection(u'FinData').document(u'Other')
            finIndexPath = finCorePath.collection(u'FinData').document(u'FinIndexPath')
            fsHTMLPath = htmlPath.document(u'FS')
            companyHTMLPath = htmlPath.document(u'CompanyInfo')
            saveCompanyDataToFireStore = SaveCompanyDataToFireStore(companyCorePath,finCorePath,bsPath,plPath,cfPath,otherPath,fsHTMLPath,companyHTMLPath,finIndexPath)
            saveCompanyDataToFireStore.save_company_data(coreData,detailData,finIndexData,formCode.value)
            forFirestoreSearchIndexDict_name[coreData.JCN] = coreData.simpleCompanyNameInJP
            forFirestoreSearchIndexDict_secCode[coreData.JCN] = coreData.SecurityCodeDEI
        try:
            shutil.move(F'{xbrl_files_path_parent}{folder_name}',"D:TEMP_XBRL_Download//")
        except:
            try:
                shutil.rmtree(F'{xbrl_files_path_parent}{folder_name}')
            except:pass
        print(f'{i} / {fainalIndex}')
    db = firestore.client()
    db.collection(u'SearchIndex').document("CompanyName_JP").set(forFirestoreSearchIndexDict_name,merge=True)
    db.collection(u'SearchIndex').document("SecCode").set(forFirestoreSearchIndexDict_secCode,merge=True)
        