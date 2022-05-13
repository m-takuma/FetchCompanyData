from datetime import datetime
from unittest import result
from arelle import ModelDtsObject
from arelle import ModelXbrl
from arelle import XbrlConst
import Const
import MySQLdb
from Const import FinDoc_Const as findoc_con
import jaconv

class Model:
    values = {}
    def __init__(self) -> None:
        self.values = {}
    def followLink(self,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept,relation,linkRole:list):
        relModels:ModelDtsObject.ModelRelationship = modelXbrl.relationshipSet(relation)
        for relModel in relModels.fromModelObject(modelObject):
            if relModel.linkrole in linkRole:
                for fact in modelXbrl.facts:
                    if fact.concept.qname == relModel.toModelObject.qname:
                        self.values[fact.concept.qname.__str__()] = fact.value
                        break
                self.followLink(modelXbrl,relModel.toModelObject,relation,linkRole)
    
    def followLink_context(self,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept,relation,linkRole:list,context:list):
        relModels:ModelDtsObject.ModelRelationship = modelXbrl.relationshipSet(relation)
        for relModel in relModels.fromModelObject(modelObject):
            if relModel.linkrole in linkRole:
                for fact in modelXbrl.facts:
                    if fact.concept.qname == relModel.toModelObject.qname and fact.contextID in context:
                        self.values[fact.concept.qname.__str__()] = fact.value
                        break
                self.followLink_context(modelXbrl,relModel.toModelObject,relation,linkRole,context)
    
    def strptime(self,date_str) -> datetime:
        tdatetime = datetime.strptime(date_str,'%Y-%m-%d')
        tdate = datetime(tdatetime.year,tdatetime.month,tdatetime.day)
        return tdate

    
    def mysql_run(self,query,args=None) -> list|None:
        results = None
        conn:MySQLdb.connections.Connection = MySQLdb.connect(
            user = 'root',
            host = '127.0.0.1',
            port = 3306,
            db='companydb'
        )
        cursor:MySQLdb.cursors.Cursor = conn.cursor()
        try:
            cursor.execute(query=query,args=args)
            results = cursor.fetchall()
        except MySQLdb.IntegrityError as integrityError:
            print(f"{integrityError} -> UQ重複")
        except Exception as err:
            print(f"{err} -> 想定外のエラー")
        cursor.close()
        conn.commit()
        conn.close()
        return results
    
    def SELECT_mysql(self,conn,query,args=None) -> list|None:
        results = None
        cursor:MySQLdb.cursors.Cursor = conn.cursor()
        try:
            cursor.execute(query=query,args=args)
            results = cursor.fetchall()
        except Exception as err:
            print(f"{err} -> 想定外のエラー")
        return results
    
    def UPDATE_mysql(self,conn,query,args=None):
        cursor:MySQLdb.cursors.Cursor = conn.cursor()
        try:
            cursor.execute(query=query,args=args)
        except Exception as err:
            print(f"{err} -> 想定外のエラー")
    
    def INSERT_mysql(self,conn,query,args=None):
        cursor:MySQLdb.cursors.Cursor = conn.cursor()
        try:
            cursor.execute(query=query,args=args)
        except Exception as err:
            print(f"{err} -> 想定外のエラー")



        



class ModelCompany(Model):
    values = {}
    def __init__(self,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept,jcn,secCode,update=False) -> None:
        super().__init__()
        super().followLink(modelXbrl,modelObject,Const.dimension,[Const.link_role_DEI])
        self.init(jcn,secCode,update)

    def init(self,jcn,secCode,update):
        self.jcn = jcn
        self.nameInJP = self._nameInJP(self.values["jpdei_cor:FilerNameInJapaneseDEI"])
        self.nameInENG = self.values["jpdei_cor:FilerNameInEnglishDEI"]
        self.secCode = self._secCode(secCode)
        self.EDINETCode = self.values["jpdei_cor:EDINETCodeDEI"]
        id = self.id(jcn)
        if id == None:
            self.saveToMysql()
        elif update == True:
            self.updateToMysql(id)
        else:
            pass

    def saveToMysql(self):
        query = "INSERT INTO company VALUES (null,%s,%s,%s,%s,%s)"
        args = (self.jcn,self.nameInJP,self.nameInENG,self.secCode,self.EDINETCode)
        super().mysql_run(query=query,args=args)
        
    
    def updateToMysql(self,id):
        query = "UPDATE company SET companyNameInJP = %s, companyNameInENG = %s, secCode = %s WHERE id = %s"
        args = (
            self.nameInJP,
            self.nameInENG,
            self.secCode,
            id
        )
        super().mysql_run(query=query,args=args)
        
    
    def id(self,jcn) -> int|None:
        query = "SELECT * FROM company WHERE jcn = %s LIMIT 0,10"
        args = (jcn,)
        results = super().mysql_run(query=query,args=args)
        
        if results == None:
            raise Exception(f"company -> None {self.jcn}")
        elif len(results) == 0:
            return None
        else:
            result = results[0]
            id = result[0]
            return id
    
    def _nameInJP(self,nameInJP:str) -> str:
        tempName:str = nameInJP.replace(" ","")#半角スペースなくす
        tempName = tempName.replace("　","")#全角スペースなくす
        tempName = tempName.replace("・","")#「・」なくす
        tempName = tempName.replace("株式会社","")#「株式会社」なくす
        tempName = jaconv.h2z(text=tempName,ascii=True,digit=True)
        return tempName
    
    def _secCode(self,secCode:str|None) -> str|None:
        if secCode == None:
            return None
        else:
            return secCode[:-1]

            

class ModelFinDoc(Model):
    values = {}
    def __init__(self,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept,company_id,docID,docType,update=False) -> None:
        super().__init__()
        super().followLink(modelXbrl,modelObject,Const.dimension,[Const.link_role_DEI])
        self.init(company_id,docID,docType,update)

    def init(self,company_id,docID,docType,update):
        self.company_id:int = company_id
        self.typeOfCurrentPeriod_id:int = self.typeOfCurrentPeriod()
        self.industryCodeDEI_id:int = self.industryCodeDEI()
        self.docID:str = docID
        self.currentFiscalYearStartDate = super().strptime(self.values[findoc_con.currentFiscalYearStartDate])
        self.currentFiscalYearEndDate = super().strptime(self.values[findoc_con.currentFiscalYearEndDateDEI])
        self.currentPeriodEndDate = super().strptime(self.values[findoc_con.currentPeriodEndDate])
        self.isConsolidated = self._isConsolidated()
        self.accountingStandard_id = self._accountingStandard()
        self.docType = docType

        id = self.id(docID)
        if id == None:
            self.saveToMysql()
        elif update == True:
            self.updateToMysql(id)
        else:
            pass
        

    
    def saveToMysql(self):
        query = "INSERT INTO fin_doc VALUES (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = (
            self.company_id,
            self.typeOfCurrentPeriod_id,
            self.industryCodeDEI_id,
            self.docID,
            self.currentFiscalYearStartDate,
            self.currentFiscalYearEndDate,
            self.currentPeriodEndDate,
            self.isConsolidated,
            self.accountingStandard_id,
            self.docType
        )
        super().mysql_run(query=query,args=args)
        
    
    def updateToMysql(self,id):
        query = "UPDATE fin_doc SET company_id = %s, currentPeriodType_id = %s, industryCodeDEI_id = %s, docID = %s, currentFiscalYearStartDate = %s, currentFiscalYearEndDate = %s, currentPeriodEndDate = %s, isConsolidated = %s, accountingStandard = %s, docType = %s WHERE id = %s"
        args = (
            self.company_id,
            self.typeOfCurrentPeriod_id,
            self.industryCodeDEI_id,
            self.docID,
            self.currentFiscalYearStartDate,
            self.currentFiscalYearEndDate,
            self.currentPeriodEndDate,
            self.isConsolidated,
            self.accountingStandard_id,
            self.docType,
            id
        )
        super().mysql_run(query=query,args=args)
        
    
    def id(self,docID):
        query = "SELECT id FROM fin_doc WHERE docID = %s LIMIT 0,10"
        args = (docID,)
        results = super().mysql_run(query=query,args=args)
        
        if results == None:
            raise Exception(f"finDoc id -> None {self.docID}")
        elif len(results) == 0:
            return None
        else:
            result = results[0]
            id = result[0]
            return id

    
    def typeOfCurrentPeriod(self) -> int:
        typeOfCurrentPeriod = self.values[findoc_con.typeOfCurrentPeriod]
        query = "SELECT * FROM current_period_type WHERE code = %s LIMIT 0,10"
        args = (typeOfCurrentPeriod,)
        results = super().mysql_run(query=query,args=args)
        
        if results == None:
            raise Exception(f"finDoc typeOfCurrentPeriod -> None {self.docID}")
        elif len(results) == 0:
            return -1
        else:
            result = results[0]
            id = result[0]
            return id
    
    def industryCodeDEI(self) -> int:
        query = "SELECT * FROM industry_code_dei WHERE code = %s LIMIT 0,10"
        args = ()
        if self.values[findoc_con.isConsolidated] == "true":
            industryCode = self.values[findoc_con.industryCodeDEI_Consolidated]
            args = (industryCode,)
        elif self.values[findoc_con.isConsolidated] == "false":
            industryCode = self.values[findoc_con.industryCodeDEI_NonConsolidated]
            args = (industryCode,)
        else:
            raise Exception(f"finDoc industryCodeDEI -> isConsolidatedのXBRLデータがない {self.docID}")
        results = super().mysql_run(query=query,args=args)
        
        if results == None:
            raise Exception(f"finDoc industryCodeDEI -> None {self.docID}")
        elif len(results) == 0:
            print("[Error]industryCodeDEI")
            return -1
        else:
            result = results[0]
            id = result[0]
            return id

    def _isConsolidated(self) -> int:
        if self.values[findoc_con.isConsolidated] == "true":
            return 1
        elif self.values[findoc_con.isConsolidated] == "false":
            return 0
        else:
            raise Exception(f"finDoc _isConsolidated -> isConsolidatedのXBRLデータがない {self.docID}")
    
    def _accountingStandard(self) -> int:
        query = "SELECT * FROM accounting_standard WHERE code = %s LIMIT 0,10"
        args = (self.values[findoc_con.accountingStandards],)
        results = super().mysql_run(query=query,args=args)
        
        if results == None:
            raise Exception(f"finDoc _accountingStandard -> None {self.docID}")
        elif len(results) == 0:
            return -1
        else:
            result = results[0]
            id = result[0]
            return id


class ModelFinData(Model):
    values = {}
    def __init__(self,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept,findoc_id,isConsolidated,dimension_id,typeOfCurrentPeriod_id,linkRoles:list) -> None:
        super().__init__()
        # Mysqlに接続する
        conn:MySQLdb.connections.Connection = MySQLdb.connect(
            user = 'root',
            host = '127.0.0.1',
            port = 3306,
            db='companydb'
        )
        self.values = {}
        if typeOfCurrentPeriod_id == 1:#通期
            context = ([Const.current_i_consolidated,Const.current_d_consolidated] if isConsolidated == 1 else [Const.current_i_non_consolidated,Const.current_d_non_consolidated])
        elif typeOfCurrentPeriod_id in [3,4,5,6,7]:#四半期:
            context = ([Const.current_q_i_consolidated,Const.current_q_d_consolidated] if isConsolidated == 1 else [Const.current_q_i_non_consolidated,Const.current_q_d_non_consolidated])
        else:
            raise Exception(f"finData __init__ -> period_id が想定外 {findoc_id}")
        self.followLink_context_FinData(conn,modelXbrl,modelObject,Const.presentation,linkRoles,context)
        for key in self.values.keys():
            self.init(conn,key,findoc_id,isConsolidated,dimension_id)
            id = self.id(conn)
            if id == None:
                self.saveToMysql(conn)
            else:
                pass
        conn.commit()
        conn.close()
        

    def init(self,conn,key,findoc_id,isConsolidated,dimension_id):
        self.finDoc_id = findoc_id
        self.accountLabel_id = self._accountLabel_id(conn,self.values[key][0])
        self.context_id = self._context_id(conn,self.values[key][2])
        self.dimension_id = self._dimension_id(conn,dimension_id)
        self.ammount = self.values[key][1]
        self.isConsolidated = isConsolidated
    
    def followLink_context_FinData(self, conn,modelXbrl: ModelXbrl.ModelXbrl, modelObject: ModelDtsObject.ModelConcept, relation, linkRole: list, context: list):
        relModels:ModelDtsObject.ModelRelationship = modelXbrl.relationshipSet(relation)
        for relModel in relModels.fromModelObject(modelObject):
            if relModel.linkrole in linkRole:
                for fact in modelXbrl.facts:
                    if fact.concept.qname == relModel.toModelObject.qname and fact.contextID in context:
                        _ = ModelAccountLabel(conn,modelXbrl,relModel.toModelObject)
                        self.values[fact.concept.qname.__str__()] = (fact.concept.qname.__str__(),fact.value,fact.contextID)
                        break
                self.followLink_context_FinData(conn,modelXbrl,relModel.toModelObject,relation,linkRole,context)
    
    def saveToMysql(self,conn):
        query = "INSERT INTO fin_data VALUES (null,%s,%s,%s,%s,%s,%s)"
        args = (
            self.finDoc_id,
            self.accountLabel_id,
            self.context_id,
            self.dimension_id,
            self.ammount,
            self.isConsolidated
        )
        super().INSERT_mysql(conn,query,args)

    '''
    def updateToMysql(self,id):
        query = "UPDATE fin_data SET fin_doc_id = %s, account_label_id = %s, context_id = %s, dimension_id = %s, ammount = %s, isConsolidated = %s WHERE id = %s"
        args = (
            self.finDoc_id,
            self.accountLabel_id,
            self.context_id,
            self.dimension_id,
            self.ammount,
            self.isConsolidated,
            id
        )
        super().mysql_run(query=query,args=args)
        
    '''
    def _accountLabel_id(self,conn,qname):
        query = "SELECT id FROM account_label WHERE qname = %s"
        args = (qname,)
        results = super().SELECT_mysql(conn,query,args)
        
        if results == None:
            print(f"_accountLabel_id -> None {self.finDoc_id}")
            raise Exception(f"_accountLabel_id -> None {self.finDoc_id}")
        elif len(results) == 0:
            print(f"_accountLabel_id -> len0 {self.finDoc_id}")
            raise Exception(f"_accountLabel_id -> len0 {self.finDoc_id}")
        else:
            result = results[0]
            id = result[0]
            return id

    def _context_id(self,conn,code):
        query = "SELECT id FROM context WHERE code = %s"
        args = (code,)
        results = super().SELECT_mysql(conn,query,args)
        
        if results == None:
            print(f"_context_id -> None {self.finDoc_id}")
            raise Exception(f"_context_id -> None {self.finDoc_id}")
        elif len(results) == 0:
            print(f"_context_id -> len0 {self.finDoc_id}")
            raise Exception(f"_context_id -> len0 {self.finDoc_id}")
        else:
            result = results[0]
            id = result[0]
            return id

    def _dimension_id(self,conn,code):
        query = "SELECT id FROM dimension WHERE code = %s"
        args = (code,)
        results = super().SELECT_mysql(conn,query,args)
        
        if results == None:
            print(f"_dimension_id -> None {self.finDoc_id}")
            raise Exception(f"_dimension_id -> None {self.finDoc_id}")
        elif len(results) == 0:
            print(f"_dimension_id -> len0 {self.finDoc_id}")
            raise Exception(f"_dimension_id -> len0 {self.finDoc_id}")
        else:
            result = results[0]
            id = result[0]
            return id
    
    def id(self,conn):
        query = "SELECT id FROM fin_data WHERE fin_doc_id = %s and account_label_id = %s and context_id = %s and dimension_id = %s and ammount = %s and isConsolidated = %s"
        args = (
            self.finDoc_id,
            self.accountLabel_id,
            self.context_id,
            self.dimension_id,
            self.ammount,
            self.isConsolidated
        )
        results = super().SELECT_mysql(conn,query,args)
        
        if results == None:
            raise Exception(f"_dimension_id -> None {self.finDoc_id}")
        elif len(results) == 0:
            return None
        else:
            result = results[0]
            id = result[0]
            return id



class ModelAccountLabel(Model):
    def __init__(self,conn,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept) -> None:
        super().__init__()
        qname = modelObject.qname.__str__()
        label = modelObject.label(lang='ja')
        self.init(qname,label)
        #ここで保存、検索
        id = self.id(conn)
        if id == None:
            self.saveToMysql(conn)
        else:
            self.updateToMysql(conn,id)
    
    def init(self,qname,label):
        self.qname = qname
        self.labelName = label

    def saveToMysql(self,conn):
        query = "INSERT INTO account_label VALUES (null,%s,%s)"
        args = (
            self.qname,
            self.labelName
        )
        super().SELECT_mysql(conn,query,args)#mysql_run(query=query,args=args)
        
    
    def updateToMysql(self,conn,id):
        query = "UPDATE account_label SET qname = %s, labelName = %s WHERE id = %s"
        args = (
            self.qname,
            self.labelName,
            id
        )
        super().UPDATE_mysql(conn,query=query,args=args)
        

    def id(self,conn) -> int|None:
        query = "SELECT * FROM account_label WHERE qname = %s LIMIT 0,10"
        args = (self.qname,)
        results = super().SELECT_mysql(conn,query,args)
        
        if results == None:
            raise Exception(f"AccountLabel id -> None")
        elif len(results) == 0:
            return None
        else:
            result = results[0]
            id = result[0]
            return id

class ModelContext:
    def __init__(self) -> None:
        self.init()

    def init(self):
        self.code = ""
        self.name = ""

class ModelDimension:
    def __init__(self) -> None:
        self.init()

    def init(self):
        self.code = ""
        self.name = ""


