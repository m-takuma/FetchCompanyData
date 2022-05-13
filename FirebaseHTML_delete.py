import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate('C://Users//taku3//Dropbox//Biz//FetchCompanyData//corporateanalysishubapp-firebase-adminsdk-n8sd4-07e702dbc7.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
class fitchData:
    def fitchJCN(self):
        #ここで全件取得
        cos = db.collection(u'COMPANY_v2').stream()
        for co in cos:
            try:
                docs = co.reference.collection('HTML').stream()
                for doc in docs:
                    doc.reference.delete()              
            except:
                pass
        '''
        for doc in docs:
            self.fitchFinDocs(doc.id)
            '''
    
    def fitchFinDocs(self,JCN:int):
        docs = db.collection(u'COMPANY_v2').document(f'{JCN}').collection(u'FinDoc').stream()
        for doc in docs:
            self.fitchIFRS_data(JCN,doc.id)

    def fitchIFRS_data(self,JCN:int,doc_id:str):
        doc = db.collection(u'COMPANY_v2').document(f'{JCN}').collection(u'FinDoc').document(f'{doc_id}')
        if doc.get().to_dict()["AccountingStandard"] == "IFRS":
            self.change_data(JCN,doc_id)
    
    def change_data(self,JCN:int,doc_id:str):
        doc = db.collection(u'COMPANY_v2').document(f'{JCN}').collection(u'FinDoc').document(f'{doc_id}').collection(u'FinData').document(u'FinIndexPath')
        doc_data = doc.get().to_dict()["NonCurrentLabilitiesIFRS"]
        doc.set({u'NonCurrentLiabilitiesIFRS': doc_data},merge=True)
        
        doc.update({u'NonCurrentLabilitiesIFRS': firestore.DELETE_FIELD})




    


if __name__ == "__main__":
    fitch_data = fitchData()
    fitch_data.fitchJCN()
