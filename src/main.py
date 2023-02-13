from enum import Enum, auto
import shutil
import edinet
import file_manager
import const
import glob
import os
from ..Project.ParseXbrl import parseXBRL


class Mode(Enum):
    PC = auto()
    API = auto()


def parse(path, doc: edinet.EdinetResultDocument):
    file_paths = glob.glob(path)
    # 解析する
    for file_path in file_paths:
        parseXBRL(file_path, doc.jcn, doc.sec_code, doc.doc_id, 1)
    try:
        # ここで行うことは解析が終わったフォルダを別フォルダに移動すること
        shutil.move(os.path.dirname(path), "G:XBRL_For_Python_Did_Parse//")
    except Exception:
        pass


if __name__ == "__main__":
    # 実行形式を決める
    mode = Mode.PC
    # 取得する書類を決める
    form_code = edinet.FormCode.YHO
    # 検索日時を決める
    begin_date = None
    end_date = None
    # 証券コードの指定をする
    sec_codes = None  # []

    if mode == Mode.API:
        result = edinet.fetch_edinet_xbrldocs(begin_date, end_date, form_code, sec_codes)  # noqa: E501
        edinet.download_edinet_xbrldocs(
            const.DOWNLOAD_XBRL_PATH,
            result.doc_id_list,
            file_manager.find_all_xbrldir(const.DOWNLOAD_XBRL_PATH + "//")
        )
    dirs = file_manager.find_all_xbrldir(const.DOWNLOAD_XBRL_PATH + "//")
