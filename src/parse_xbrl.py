from arelle import Cntlr, ModelManager, ModelXbrl, ModelDtsObject
import const
from edinet import EdinetResultDocument as Doc


def parse_xbrl(file_path, doc: Doc, docType):
    cntlr = Cntlr.Cntlr(logFileName='logToPrint')
    # XBRLのモデルを作成
    model_manager = ModelManager.initialize(cntlr=cntlr)
    model_xbrl: ModelXbrl.ModelXbrl = model_manager.load(file_path)

    # 解析して保存
    # 会社と書類データを保存する
    findoc = None
    for i, model_obj in enumerate(model_xbrl.modelObjects):
        if type(model_obj) is ModelDtsObject.ModelConcept and str(model_obj.qname) == const.dei_root:  # noqa: E501
            company = Corporate(model_xbrl, model_obj, doc)
            # findoc = ModelFinDoc(modelXbrl,model_obj,company.id(company.jcn),docID,docType,update=False)
    if findoc is None:  # うまくXBRLが処理できなかった可能性
        print(f"{doc.doc_id} XBRLの解析に失敗しました {file_path}")
        return None
    # 財務諸表のデータを保存する
    for i, modelObject in enumerate(model_xbrl.modelObjects):
        pass
        '''
        if findoc.typeOfCurrentPeriod_id == 1:  # 通期
            parseYHO(modelXbrl,modelObject,findoc)
        elif findoc.typeOfCurrentPeriod_id in [3,4,5,6,7]:#四半期
            parseYNPO(modelXbrl,modelObject,findoc)
        '''


def follow_link(
    model_xbrl: ModelXbrl.ModelXbrl,
    model_obj: ModelDtsObject.ModelConcept,
    relation,
    link_roles: list,
    result: dict
        ) -> dict:
    rel_models: ModelDtsObject.ModelRelationship = model_xbrl.relationshipSet(relation)  # noqa: E501
    for rel_model in rel_models.fromModelObject(model_obj):
        if rel_model.linkrole in link_roles:
            for fact in model_xbrl.facts:
                if fact.concept.qname == rel_model.toModelObject.qname:
                    result[fact.concept.qname.__str__()] = fact.value
                    break
            follow_link(model_xbrl, rel_model.toModelObject, relation, link_roles, result)  # noqa: E501
    return result

class Model:
    def followLink_context(self,modelXbrl:ModelXbrl.ModelXbrl,modelObject:ModelDtsObject.ModelConcept,relation,linkRole:list,context:list):
        relModels:ModelDtsObject.ModelRelationship = modelXbrl.relationshipSet(relation)
        for relModel in relModels.fromModelObject(modelObject):
            if relModel.linkrole in linkRole:
                for fact in modelXbrl.facts:
                    if fact.concept.qname == relModel.toModelObject.qname and fact.contextID in context:
                        self.values[fact.concept.qname.__str__()] = fact.value
                        break
                self.followLink_context(modelXbrl,relModel.toModelObject,relation,linkRole,context)


class Corporate:
    def __init__(
        self,
        model_xbrl: ModelXbrl.ModelXbrl,
        model_obj: ModelDtsObject.ModelConcept,
        doc: Doc
            ) -> None:
        super().__init__()
        resulut: dict = follow_link(model_xbrl, model_obj, const.dimension, [const.link_role_DEI])  # noqa: E501
        self.setup_corporate(doc, resulut)

    def setup_corporate(self, doc: Doc, values):
        self.jcn = doc.jcn
        self.name_jp = self.formatter_name_jp(values["jpdei_cor:FilerNameInJapaneseDEI"])  # noqa: E501
        self.name_eng = values["jpdei_cor:FilerNameInEnglishDEI"]
        self.sec_code = self.formatter_sec_code(doc.sec_code)
        self.edinet_code = values["jpdei_cor:EDINETCodeDEI"]

    def formatter_name_jp(self, name_jp: str) -> str:
        formated_name: str = name_jp.replace(" ", "")  # 半角スペースなくす
        formated_name = formated_name.replace("　", "")  # 全角スペースなくす
        formated_name = formated_name.replace("・", "")  # 「・」なくす
        formated_name = formated_name.replace("株式会社", "")  # 「株式会社」なくす
        formated_name = jaconv.h2z(text=formated_name, ascii=True, digit=True)
        return formated_name

    def formatter_sec_code(self, sec_code: str | None) -> str | None:
        if sec_code is None:
            return None
        else:
            return sec_code[:-1]
