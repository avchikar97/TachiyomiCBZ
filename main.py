import argparse
import os
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--tachiyomi-path", help="file path to the Tachiyomi folder", default=os.path.dirname(os.path.realpath(__file__)))
parser.add_argument("-d", "--delete", help="delete the original chapter folder + images once the .cbz file has been created", action="store_true")
parser.add_argument("-t", "--test", help="print the paths of all the .cbz files to be created but do not create them", action="store_true")
parser.add_argument("-v", "--verbosity", help="level of verbosity [0|1|2|3]. Default = 0 (silent)", default=0)

args = parser.parse_args()
tachiyomi_path = args.tachiyomi_path
isDelete = args.delete
isTest = args.test
curr_verbosity = int(args.verbosity)

def VERBOSITY_PRINT(str_verbosity:int, str:str):
    if(str_verbosity <= curr_verbosity):
        print(str)

def zipfiles_source(current_path:str):
    # for each `comic`
    for comic_name in os.listdir(os.getcwd()): # enter each comic in each source
        if(os.path.isdir(comic_name)):
            os.chdir(comic_name)
            VERBOSITY_PRINT(2, f"Entering {os.getcwd()}")

            # for each `chapter` in `comic`
            for chapter_name in os.listdir(os.getcwd()):
                if(os.path.isdir(chapter_name)):
                    # create cbz of format "chapter_name.cbz" and contents of `chapter`
                    # -t means no cbz is created
                    if(not isTest):
                        zip_name = shutil.make_archive(chapter_name, 'zip', os.path.join(os.getcwd(), chapter_name))
                        p = Path(zip_name)
                        p.rename(p.with_suffix(".cbz"))

                    VERBOSITY_PRINT(1, str(os.path.join(os.getcwd(), f"{chapter_name}.cbz")))

                    # clean up image folders
                    if(isDelete):
                        current_chapter_full_path = os.path.join(current_path, comic_name, chapter_name)
                        VERBOSITY_PRINT(2, f"Deleting {current_chapter_full_path}")
                        shutil.rmtree(current_chapter_full_path)

            VERBOSITY_PRINT(2, f"Exiting {os.getcwd()}")
            os.chdir(os.path.dirname(os.getcwd())) # leave this comic

def zipfiles_downloads(current_path:str):
    if(os.path.isdir(current_path)):
        os.chdir(current_path)
        VERBOSITY_PRINT(2, f"Entering {os.getcwd()}")

        for source_name in os.listdir(os.getcwd()):
            if(os.path.isdir(source_name)):
                os.chdir(source_name)
                VERBOSITY_PRINT(2, f"Entering {os.getcwd()}")

                zipfiles_source(os.getcwd())

                os.chdir(os.path.dirname(os.getcwd())) # leave this source
                VERBOSITY_PRINT(2, f"Exiting {os.getcwd()}")

        os.chdir(os.path.dirname(os.getcwd())) # leave downloads
        VERBOSITY_PRINT(2, f"Exiting {os.getcwd()}")

if __name__ == "__main__":
    # Start in tachiyomi
    VERBOSITY_PRINT(3, f"tachiyomi_path = {tachiyomi_path}, isDelete = {isDelete}, isTest = {isTest}")

    # go to `downloads`
    download_path = os.path.join(tachiyomi_path, "downloads")
    if os.path.isdir(download_path):
        zipfiles_downloads(download_path)

    # repeat for 'local' (local is just a source)
    local_path = os.path.join(tachiyomi_path, "local")
    if os.path.isdir(local_path):
        os.chdir(local_path)
        VERBOSITY_PRINT(2, f"Entering {os.getcwd()}")
        zipfiles_source(local_path)
