# インポートする
from arelle import Cntlr
from arelle import ModelManager
from arelle import ModelDtsObject
from arelle import ModelValue
from arelle import XbrlConst
from arelle import ModelXbrl

import MySQLdb
import sys
from Model import Model, ModelCompany,ModelFinDoc
from Model import ModelFinData
import Const
from EDINETLoader import FetchXBRLFileClass

#テスト用
filename_for_test = "C://Users//taku3//OneDrive//デスクトップ//XBRL_test//PublicDoc//jpcrp030000-asr-001_E03061-000_2021-02-28_01_2021-05-27.xbrl"

#出力ファイル
#fo = open('C://Users//taku3//Downloads//1.txt', 'w', encoding='utf-8')

# 収集するデータの表示リンク
ConsolidatedBalanceSheet = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedBalanceSheet'
'''連結貸借対照表'''
ConsolidatedStatementOfIncome = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfIncome'
'''連結損益（及び包括利益）計算書'''
ConsolidatedStatementOfComprehensiveIncome = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfComprehensiveIncome'
'''包括利益計算書'''
ConsolidatedStatementOfCashFlows_direct = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfCashFlows-direct'
'''連結キャッシュ・フロー計算書　直接法'''
ConsolidatedStatementOfCashFlows_indirect = 'http://disclosure.edinet-fsa.go.jp/role/jppfs/rol_ConsolidatedStatementOfCashFlows-indirect'
'''連結キャッシュ・フロー計算書　間接法'''

bs_items = "jppfs_cor:BalanceSheetLineItems"
pl_items = "jppfs_cor:StatementOfIncomeLineItems"
pl_2_items = "jppfs_cor:StatementOfComprehensiveIncomeLineItems"
cf_items = "jppfs_cor:StatementOfCashFlowsLineItems"

def printLink(linkrol,modelObject:ModelDtsObject.ModelConcept, indent, relModels:ModelDtsObject.ModelRelationship):
    indentStr = "  ";
    linkrole = linkrol
    for i in range(indent):
        indentStr += "  ";
    for relModel in relModels.fromModelObject(modelObject):
        print(relModel.linkrole)
        if linkrole == None:
            if relModel.linkrole == ConsolidatedBalanceSheet:
                linkrole = ConsolidatedBalanceSheet
            elif relModel.linkrole == ConsolidatedStatementOfIncome:
                linkrole = ConsolidatedStatementOfIncome
            elif relModel.linkrole == ConsolidatedStatementOfComprehensiveIncome:
                linkrole = ConsolidatedStatementOfComprehensiveIncome
            elif relModel.linkrole == ConsolidatedStatementOfCashFlows_direct:
                linkrole = ConsolidatedStatementOfCashFlows_direct
            elif relModel.linkrole == ConsolidatedStatementOfCashFlows_indirect:
                linkrole = ConsolidatedStatementOfCashFlows_indirect
        
        if relModel.linkrole == linkrole:
            relModel:ModelDtsObject.ModelRelationship = relModel
            fromObject:ModelDtsObject.ModelConcept = relModel.fromModelObject
            toObject:ModelDtsObject.ModelConcept = relModel.toModelObject
            modelXbrl:ModelXbrl.ModelXbrl = toObject.modelXbrl
            print(indentStr, "from: ", relModel.fromModelObject.label(preferredLabel=None,lang='ja', linkrole=None))
            print(indentStr, "to: ", relModel.toModelObject.label(preferredLabel=relModel.preferredLabel, lang='ja', linkroleHint=relModel.arcrole))
            for fact in modelXbrl.facts:
                fact:ModelXbrl.ModelFact = fact
                if fact.qname == toObject.qname:
                    print(fact.value)
                    break
            print("\n")
            # リンクを再帰的にたどる
            printLink(linkrole, relModel.toModelObject, indent+1, relModels)
        

def parseXBRL(file_path,jcn,secCode,docID,docType):
    cntlr = Cntlr.Cntlr(logFileName='logToPrint')
    # XBRLのモデルを作成
    modelManager = ModelManager.initialize(cntlr=cntlr)
    modelXbrl:ModelXbrl.ModelXbrl = modelManager.load(file_path)

    # 解析して保存
    #会社と書類データを保存する
    findoc = None
    for i,modelObject in enumerate(modelXbrl.modelObjects):
        if type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.dei_root:
            company = ModelCompany(modelXbrl,modelObject,jcn,secCode,update=False)
            findoc = ModelFinDoc(modelXbrl,modelObject,company.id(company.jcn),docID,docType,update=False)
    if findoc == None: #うまくXBRLが処理できなかった可能性
        print(f"{docID} XBRLの解析に失敗しました {file_path}")
        return None
    #財務諸表のデータを保存する
    for i,modelObject in enumerate(modelXbrl.modelObjects):
        if findoc.typeOfCurrentPeriod_id == 1:#通期
            parseYHO(modelXbrl,modelObject,findoc)
        elif findoc.typeOfCurrentPeriod_id in [3,4,5,6,7]:#四半期
            parseYNPO(modelXbrl,modelObject,findoc)
def parseYHO(modelXbrl,modelObject,findoc):
    if findoc.isConsolidated == 1: #連結財務諸表があるときの場合
        if type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.bs_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id, [Const.link_role_ConsolidatedBalanceSheet])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.pl_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,  [Const.link_role_ConsolidatedStatementOfIncome])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.pl_2_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,  [Const.link_role_ConsolidatedStatementOfComprehensiveIncome])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.cf_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,[Const.link_role_ConsolidatedStatementOfCashFlows_direct,Const.link_role_ConsolidatedStatementOfCashFlows_indirect])
    else:#個別財務諸表のみの場合
        if type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.bs_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,  [Const.link_role_Non_ConsolidatedBalanceSheet])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.pl_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,  [Const.link_role_Non_ConsolidatedStatementOfIncome])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.cf_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,[Const.link_role_Non_ConsolidatedStatementOfCashFlows_direct,Const.link_role_Non_ConsolidatedStatementOfCashFlows_indirect])

def parseYNPO(modelXbrl,modelObject,findoc):#四半期
    if findoc.isConsolidated == 1: #連結財務諸表があるときの場合
        if type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.bs_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname), findoc.typeOfCurrentPeriod_id, [Const.link_role_QuarterlyConsolidatedBalanceSheet])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.pl_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname), findoc.typeOfCurrentPeriod_id, [Const.link_role_YearToQuarterlyEndConsolidatedStatementOfIncome])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.pl_2_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname), findoc.typeOfCurrentPeriod_id, [Const.link_role_YearToQuarterEndConsolidatedStatementOfComprehensiveIncome])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.cf_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,[Const.link_role_QuarterlyConsolidatedStatementOfCashFlows_direct,Const.link_role_QuarterlyConsolidatedStatementOfCashFlows_indirect])
    else:#個別財務諸表のみの場合
        if type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.bs_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname), findoc.typeOfCurrentPeriod_id, [Const.link_role_Quarterly_Non_ConsolidatedBalanceSheet])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.pl_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname), findoc.typeOfCurrentPeriod_id, [Const.link_role_YearToQuarterlyEnd_Non_ConsolidatedStatementOfIncome])
        elif type(modelObject) is ModelDtsObject.ModelConcept and str(modelObject.qname) == Const.cf_root:
            findata = ModelFinData(modelXbrl,modelObject,findoc.id(findoc.docID),findoc.isConsolidated,str(modelObject.qname),findoc.typeOfCurrentPeriod_id,[Const.link_role_Quarterly_Non_ConsolidatedStatementOfCashFlows_direct,Const.link_role_Quarterly_Non_ConsolidatedStatementOfCashFlows_indirect])


def fetch_jcn_secCode(file_path,jcn_dict,sec_dict) -> tuple|None:
    cntlr = Cntlr.Cntlr()
    # XBRLのモデルを作成
    modelManager = ModelManager.initialize(cntlr=cntlr)
    try:
        modelXbrl:ModelXbrl.ModelXbrl = modelManager.load(filesource=file_path)
    except:
        return None
    edinetCode = None
    for fact in modelXbrl.facts:
        fact:ModelXbrl.ModelFact = fact
        if fact.concept.qname.__str__() == "jpdei_cor:EDINETCodeDEI":
            edinetCode = fact.value
            break
    if edinetCode == None:
        return None
    else:
        try:
            jcn = jcn_dict[edinetCode]
            secCode = sec_dict[edinetCode]
            return (jcn,secCode)
        except:
            pass
        #mysql検索
        query = "SELECT jcn,secCode FROM company WHERE EDINETCode = %s"
        args = (edinetCode,)
        results = None
        # Mysqlに接続する
        conn:MySQLdb.connections.Connection = MySQLdb.connect(
            user = 'root',
            host = '127.0.0.1',
            db='companydb'
        )
        cursor:MySQLdb.cursors.Cursor = conn.cursor()
        try:
            cursor.execute(query=query,args=args)
            results = cursor.fetchall()
        except Exception as err:
            print(f"{err} -> 想定外のエラー")
        cursor.close()
        conn.close()
        if len(results) == 1:
            result = results[0]
            return (result[0],result[1])
        else:
            #edinetApi検索　過去5年間全ループ
            return FetchXBRLFileClass().search_jcn_secCode(edinetCode)

        


if __name__ == "__main__":

    #parseXBRL(filename_for_test,"6040001003380","8267","TEST",1)
    '''
    cursor.execute("SELECT * FROM dimension")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
    '''