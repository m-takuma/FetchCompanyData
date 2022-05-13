from ast import arg
import EDINETLoader
from EDINETLoader import FetchXBRLFileClass
from datetime import date
from Const import SecCodes
import glob
import ParseXbrl
import shutil
import MySQLdb
import sys
import multiprocessing

def main():

    #################
    jcn_dict = None
    sec_dict = None
    docID_list = None
    #################
    #################
    EDINET_loader = EDINETLoader.FetchXBRLFileClass()

    mode = 1
    #0 => パソコン : 1 => API
    s_date = None#date(2021,1,14)
    e_date = None#date(2021,1,14)

    seccodes = None#SecCodes.secCode_enc(secCode_list=SecCodes.ALL)
    #print(len(secCodes))

    formCode = EDINET_loader.SearchParameter.formCodeType.YNPO
    
    fetch_xbrl_file_parameter = EDINET_loader.SearchParameter(mode,s_date,e_date,seccodes,formCode)
    #################
    ###ダウンロードする or フォルダ内のファイル###
    data = EDINET_loader.fetchXbrlFile(parameter=fetch_xbrl_file_parameter)
    jcn_dict = data.jcn_str_dict
    sec_dict = data.secCode_str_dict
    edinet_dict = data.edinetCode
    docID_list = data.doc_id_list
    #################
    ###解析前の準備###
    '''
    ###MySqlから取得する###
    results = get_docID_fromMysql()
    docID_list = results[0]
    edinet_dict = results[1]
    ######################
    '''
    xbrl_files_path_parent = "G:XBRL_For_Python_Parse//"
    xbrl_files_path_child = "//XBRL//PublicDoc//*.xbrl"
    fainalIndex = len(docID_list) - 1
    args = [
            [
                i,
                docID,
                xbrl_files_path_parent,
                xbrl_files_path_child,
                formCode,
                jcn_dict,
                sec_dict,
                edinet_dict,
                fainalIndex
            ] for i, docID in enumerate(docID_list)
        ]
    #wrapper_parse(args[0])
    p = multiprocessing.Pool(processes=5)
    p.map(wrapper_parse,args)

def parse(index,docID,parent,child,formCode,jcn_dict,sec_dict,edinet_dict,fainalIndex):
    folder_name = docID
    file_paths = glob.glob(f'{parent}{folder_name}{child}')

    formCodeType = FetchXBRLFileClass.SearchParameter.formCodeType

    docType = (1 if formCode == formCodeType.YHO or formCode == formCodeType.YNPO else -1)
    if docType == -1:
            raise Exception("")

    ###解析する###
    for file_path in file_paths:
        key = edinet_dict.get(folder_name)
        result = jcn_secCode(key,file_path,jcn_dict,sec_dict)
        if result == None:
            print(f"jcnが見つかりません：{file_path}")
        else:
            jcn = result[0]
            secCode = result[1]
            ParseXbrl.parseXBRL(file_path,jcn,secCode,folder_name,docType)
    try:
        pass
        #shutil.move(F'{xbrl_files_path_parent}{folder_name}',"D:TEMP_XBRL_Download//")
        shutil.move(F'{parent}{folder_name}',"G:XBRL_For_Python_Did_Parse//")
    except:
        try:
            pass
            #shutil.rmtree(F'{parent}{folder_name}')
        except:pass
    print(f'{index} / {fainalIndex}')

def wrapper_parse(args):
    return parse(*args)
def jcn_secCode(key,filepath,jcn_dict,sec_dict) -> tuple|None:
    try:
        jcn = jcn_dict[key]
        secCode = sec_dict[key]
        return (jcn,secCode)
    except:
        return ParseXbrl.fetch_jcn_secCode(filepath,jcn_dict,sec_dict)

def get_docID_fromMysql():
    files = []
    edinet_dict = {}
    query = "SELECT company_id,docID FROM fin_doc"
    results = None
    # Mysqlに接続する
    conn:MySQLdb.connections.Connection = MySQLdb.connect(
        user = 'root',
        host = '127.0.0.1',
        db='companydb'
    )
    cursor:MySQLdb.cursors.Cursor = conn.cursor()
    try:
        cursor.execute(query=query)
        results = cursor.fetchall()
        for result in results:
            query = "SELECT EDINETCode FROM company WHERE id = %s"
            args = (result[0],)
            cursor.execute(query,args)
            edinet = cursor.fetchone()
            files.append(result[1])
            edinet_dict[result[1]] = edinet[0]
        print(edinet_dict)
        print(files)
    except Exception as err:
        print(f"{err} -> 想定外のエラー")
    cursor.close()
    conn.commit()
    conn.close()
    return (files,edinet_dict)



if __name__ == "__main__":
    main()


