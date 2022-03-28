import datetime
from weakref import ref
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from FetchCompanyData import FetchXBRLFileClass
from 銘柄コード import SecCodeClass
from AccountClass import CoreData


class RealtimeDatabase:
    # Fetch the service account key JSON file contents
    

    # Initialize the app with a service account, granting admin privileges
    

    def save_data_to_RealtimeDatabase(self,data,metaData,root="SearchIndex"):
        ref_main = db.reference(root).child("main")
        ref_main.update(data)
        ref_meta = db.reference(root).child("meta")
        ref_meta.set(metaData)


    def secCode_enc(self,secCode_list) -> list:
        ls_result = []
        for secCode in secCode_list:
            ls_result.append(str(secCode * 10))
        return ls_result
    def createSearchIndex(self):
        cred = credentials.Certificate('C://Users//taku3//Dropbox//Biz//FetchCompanyData//corporateanalysishubapp-firebase-adminsdk-n8sd4-07e702dbc7.json')
        firebase_admin.initialize_app(cred,{'databaseURL':'https://corporateanalysishubapp-default-rtdb.firebaseio.com/'})
        fetch = FetchXBRLFileClass()
        secCodes = self.secCode_enc(SecCodeClass.ALL)
        parameter = fetch.SearchParameter(mode=0,s_date=None,e_date=None,secCode_list=secCodes,formCode=fetch.SearchParameter.formCodeType.YHO)
        result:FetchXBRLFileClass.ResultData = fetch.fetchXbrlFile(parameter)
        co_name_dict = self.encCompanyName(result.companyName_dict)
        secCode_dict = result.secCode_str_dict
        jcn_dict = result.jcn_str_dict
        print(len(jcn_dict.keys()))
        metaData = {"lastModified":datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d')}
        company_dict = {}
        for key in jcn_dict.keys():
            try:
                secCode = secCode_dict[key][:-1]
            except:
                secCode = secCode_dict[key]
            company_dict[jcn_dict[key]] = {
                    "secCode":secCode,
                    "companyName":co_name_dict[key]
                }
        self.save_data_to_RealtimeDatabase(company_dict,metaData)
    
    def encCompanyName(self,name_dict:dict) -> dict:
        new_name_dict = {}
        for key in name_dict.keys():
            new_name_dict[key] = CoreData().create_simpleCompanyNameInJP(name_dict[key])
        return new_name_dict

if __name__ == "__main__":
    RealtimeDatabase().createSearchIndex()