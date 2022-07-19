import argparse
import os
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--tachiyomi-path", help="file path to the Tachiyomi folder")
parser.add_argument("-d", "--delete", help="flag to delete the original chapter folder + images once the .cbz file has been created. Default = no deletions", action="store_true")
parser.add_argument("-t", "--test", help="flag to only print the paths of all the .cbz files to be created but do not create them. Default = create the CBZ", action="store_true")
parser.add_argument("-c", "--clean", help="flag to clean up by deleting any .nomedia files in chapter folders that it comes across. Default = no cleanup", action="store_true")
parser.add_argument("-v", "--verbosity", help="level of verbosity [0|1|2|3]. Default = 0 (silent)", default=0)

args = parser.parse_args()
tachiyomi_path = str(args.tachiyomi_path)
isDelete = bool(args.delete)
isTest = bool(args.test)
isCleanup = bool(args.clean)
curr_verbosity = int(args.verbosity)

def VERBOSITY_PRINT(str_verbosity:int, str:str):
    if(str_verbosity <= curr_verbosity):
        print(str)

def cbz_folder(folder_name:str):
    nomedia_path = os.path.join(os.getcwd(), folder_name, ".nomedia")
    if(isCleanup and os.path.exists(nomedia_path)):
        VERBOSITY_PRINT(1, f"Deleting {str(nomedia_path)}")
        if(not isTest): # message without deleting if this is a test run
            os.remove(nomedia_path)

    # create cbz of format "folder_name.cbz" and contents of `folder`
    # -t means no cbz is created
    if(not isTest):
        zip_name = shutil.make_archive(folder_name, 'zip', os.path.join(os.getcwd(), folder_name))
        p = Path(zip_name)
        p.rename(p.with_suffix(".cbz"))

    created_cbz_name = str(os.path.join(os.getcwd(), f"{folder_name}.cbz"))
    VERBOSITY_PRINT(1, f"Creating {created_cbz_name}")

    # clean up image folders if -d
    if(isDelete):
        current_chapter_full_path = os.path.join(os.getcwd(), folder_name)
        VERBOSITY_PRINT(2, f"Deleting {current_chapter_full_path}")
        if(not isTest):
            shutil.rmtree(current_chapter_full_path)

def cbz_search(curr_dirr_name, folder_list):
    VERBOSITY_PRINT(1, f"Entering {curr_dirr_name}")
    os.chdir(curr_dirr_name)

    for folder_name in folder_list:
        directory_list = os.listdir(os.path.join(os.getcwd(), folder_name))
        directory_list = [directory for directory in directory_list if os.path.isdir(os.path.join(folder_name, directory))]

        if directory_list: # the folder being examined has directories in it - it is not a chapter so explore the directories
            cbz_search(folder_name, directory_list)
        else: # the folder_name is a chapter that can be CBZd
            cbz_folder(folder_name)

    VERBOSITY_PRINT(1, f"Exiting {os.getcwd()}")
    os.chdir(os.path.dirname(os.getcwd())) # done here leave this folder (could be the comic, could be the source)

if __name__ == "__main__":
    # Start in tachiyomi
    VERBOSITY_PRINT(3, f"tachiyomi_path = {tachiyomi_path}, isDelete = {isDelete}, isTest = {isTest}")

    directory_list = os.listdir(tachiyomi_path)
    directory_list = [directory for directory in directory_list if os.path.isdir(os.path.join(tachiyomi_path, directory))]
    if directory_list:
        cbz_search(tachiyomi_path, directory_list)
