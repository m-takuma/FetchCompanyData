from datetime import date, timedelta
import const
import requests
from enum import Enum


class FormCode(Enum):
    YHO = "有価証券報告書"
    YHO_T = "訂正有価証券報告書"
    YNPO = "四半期報告書"
    YNPO_T = "訂正四半期報告書"

    def number(self) -> str | None:
        if self == FormCode.YHO:
            return "030000"
        elif self == FormCode.YHO_T:
            return "030001"
        elif self == FormCode.YNPO:
            return "043000"
        elif self == FormCode.YNPO_T:
            return "043001"
        else:
            return None


class SearchParameter:
    def __init__(
        self,
        begin_date,
        end_date,
        sec_codes: list,
        form_code: FormCode
            ) -> None:
        self.start_date = begin_date
        self.end_date = end_date
        self.sec_codes = sec_codes
        self.form_code = form_code


class EdinetResultDocument:
    def __init__(
        self,
        jcn: str,
        name: str,
        sec_code: str,
        edinet_code: str,
        doc_id: str
            ) -> None:
        self.jcn = jcn
        self.name = name
        self.sec_code = sec_code
        self.edinet_code = edinet_code
        self.doc_id = doc_id


class ResultData:
    def __init__(self, doc_id_list, docs) -> None:
        self.doc_id_list = doc_id_list
        self.docs = docs


def create_edinet_document_endpoint(documentId: str) -> str:
    '''書類取得APIエンドポイント（リクエストURL）'''
    # typeは1で固定する
    return const.EDINET_API_ENDPOINT_BASE + F"documents/{documentId}?type=1"


def create_edinet_documents_endpoint(
    search_date: date,
    response_type: int
        ) -> str:
    '''書類一覧APIエンドポイント（リクエストURL）'''
    return const.EDINET_API_ENDPOINT_BASE + \
        F"documents.json?date={search_date}&type={response_type}"


def create_search_date_list(start_date, end_date) -> list:
    '''期間を指定して返す'''
    period = end_date - start_date + 1
    period = int(period.days)
    dayList = []
    for i in range(period):
        day = start_date + timedelta(days=i)
        dayList.append(day)
        if i == period - 1:
            # 期間両入
            dayList.append(day + timedelta(days=1))
    return dayList


def create_doc_id_list(
    dates: list, form_code: FormCode, sec_codes: list
        ) -> ResultData:
    '''
    期間内の条件に当てはまる書類IDをリストにして返す secCode=すべて検索の場合　None
    '''
    docs = {}
    doc_id_list = []
    finish_count = len(dates) - 1
    for index, d in enumerate(dates):
        url = create_edinet_documents_endpoint(d, 2)
        try:
            res = requests.get(url, timeout=3.5)
        except Exception as err:
            print(err)
            raise ValueError("error")
        json_data = res.json()
        if json_data["metadata"]["status"] != "200":
            status = json_data["metadata"]["status"]
            print(F"{date}:{status}")
            continue
        for num in range(0, json_data["metadata"]["resultset"]["count"]):
            ordinance_code_status = str(json_data["results"][num]["ordinanceCode"]) == "010"  # noqa: E501
            form_code_status = str(json_data["results"][num]["formCode"]) == str(form_code.value)  # noqa: E501
            sec_code = str(json_data["results"][num]["secCode"])
            should_parse = (ordinance_code_status and form_code_status and sec_codes is None) or \
                           (ordinance_code_status and form_code_status and sec_code in sec_codes)  # noqa: E501
            # 上場のみ有価証券報告書
            if should_parse:
                jcn = json_data["results"][num]["JCN"]
                name = json_data["results"][num]["filerName"]
                sec_code = json_data["results"][num]["secCode"]
                edinet_code = json_data["results"][num]["edinetCode"]
                doc_id = json_data["results"][num]["docID"]
                doc = EdinetResultDocument(
                    jcn, name, sec_code, edinet_code, doc_id
                    )
                docs[doc_id] = doc
                doc_id_list.append(doc_id)
        print(f"search_doc : {index}/{finish_count}")
    print("検索が終了しました")
    return ResultData(doc_id_list, docs)


def download_edinet_xbrldocs(download_path, doc_id_list: list, donwnloaded_doc_list: list):  # noqa: E501
    '''docListのXBRLをダウンロードする'''
    # すでにダウンロードされている書類を除く
    download_docs = list(set(doc_id_list) - set(donwnloaded_doc_list))
    print(len(download_docs))
    finish_count = len(doc_id_list)
    for index, doc_id in enumerate(download_docs):
        # time.sleep(1)
        url = create_edinet_document_endpoint(doc_id)
        filename = download_path + doc_id + ".zip"  # noqa: E501  # "G:XBRL_For_Python_Parse//" + doc_id + ".zip"
        res = requests.get(url)
        if res.status_code == 200:
            with open(filename, "wb") as file:
                for chunk in res.iter_content(chunk_size=1024):
                    file.write(chunk)
        else:
            print("失敗しました")
            print(res.status_code)
        print(f"downloaded : {index+1}/{finish_count}")
    print("ダウンロードが終了しました")


def fetch_edinet_xbrldocs(begin_date, end_date, form_code: FormCode, sec_codes) -> ResultData:  # noqa: E501
    '''期間を指定しその期間の書類を検索して、書類IDのリストと詳細データの含まれたReslutDataクラスを返す'''
    if begin_date is None or end_date is None:
        end_date = date.today()
        begin_date = date(year=end_date.year - 5, month=end_date.month, day=end_date.day)  # noqa: E501
    date_list = create_search_date_list(begin_date, end_date)
    result = create_doc_id_list(date_list, form_code, sec_codes)
    return result
