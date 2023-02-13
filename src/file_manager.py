import glob
import os
import shutil


def listdir(dir_path):
    return os.listdir(dir_path)


def unzip_files(dir_path):
    '''zipFileを展開しxbrlFileを取り出す'''
    files = []
    zip_files = glob.glob(os.path.join(dir_path, '*.zip'))
    error_files = []
    for index, zip_file in enumerate(zip_files):  # index除かない！！
        basename_without_zip = os.path.splitext(os.path.basename(zip_file))[0]
        # with zipfile.ZipFile(zip_File) as zip_f:
        try:
            shutil.unpack_archive(zip_file, f'{dir_path}//{basename_without_zip}')  # noqa: E501
            files.append(basename_without_zip)
        except Exception:
            error_files.append(basename_without_zip)
    # 不使用なzipfileを削除する
    print(f"展開できなかったfiles:{error_files}")
    for file in zip:
        os.remove(file)
    return files


def find_all_xbrldir(dir_path):
    '''フォルダを全て取得する。xbrlのフォルダをすべて取得することを想定している'''
    # path = "G:XBRL_For_Python_Parse////"
    files = listdir(dir_path)
    dirs = [f for f in files if os.path.isdir(os.path.join(dir_path, f))]
    return dirs


def find_all_xbrlfile(dir_path):
    return glob.glob(f'{dir_path}*.xbrl')
