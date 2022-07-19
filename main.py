import argparse
import os
import shutil
from pathlib import Path

DEBUGGING = True

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--tachiyomi-path", help="file path to the Tachiyomi folder", default=os.path.dirname(os.path.realpath(__file__)))
parser.add_argument("-d", "--delete", help="delete the original chapter folder once the .cbz file has been created", action="store_true")
parser.add_argument("-t", "--test", help="print the paths of all the .cbz files to be created but do not create them", action="store_true")

args = parser.parse_args()
tachiyomi_path = args.tachiyomi_path
isDelete = args.delete
isTest = args.test

def zipfiles_source(current_path:str):
    # for each `comic`
    for comic_name in os.listdir(os.getcwd()): # enter each comic in each source
        if(os.path.isdir(comic_name)):
            os.chdir(comic_name)
            print("Entering", os.getcwd())

            # for each `chapter` in `comic`
            for chapter_name in os.listdir(os.getcwd()):
                if(os.path.isdir(chapter_name)):
                    # create cbz of format "chapter_name.cbz" and contents of `chapter`
                    # -t means no cbz is created
                    if(not isTest):
                        zip_name = shutil.make_archive(chapter_name, 'zip', os.path.join(os.getcwd(), chapter_name))
                        p = Path(zip_name)
                        p.rename(p.with_suffix(".cbz"))

                    print(os.path.join(os.getcwd(), f"{chapter_name}.cbz"))

                    # clean up image folders
                    if(isDelete):
                        shutil.rmtree(os.path.join(current_path, comic_name, chapter_name))

            print("Exiting", os.getcwd())
            os.chdir(os.path.dirname(os.getcwd())) # leave this comic

def zipfiles_downloads(current_path:str):
    if(os.path.isdir(current_path)):
        os.chdir(current_path)
        print("Entering", os.getcwd())

        for source_name in os.listdir(os.getcwd()):
            if(os.path.isdir(source_name)):
                os.chdir(source_name)
                print("Entering", os.getcwd())

                zipfiles_source(os.getcwd())

                os.chdir(os.path.dirname(os.getcwd())) # leave this source
                print("Exiting", os.getcwd())

        os.chdir(os.path.dirname(os.getcwd())) # leave downloads
        print("Exiting", os.getcwd())

if __name__ == "__main__":
    # Start in tachiyomi
    if DEBUGGING:
        print(f"tachiyomi_path = {tachiyomi_path}, isDelete = {isDelete}, isTest = {isTest}")

    # go to `downloads`
    download_path = os.path.join(tachiyomi_path, "downloads")
    if os.path.isdir(download_path):
        zipfiles_downloads(download_path)

    # repeat for 'local' (local is just a source)
    local_path = os.path.join(tachiyomi_path, "local")
    if os.path.isdir(local_path):
        os.chdir(local_path)
        print("Entering", os.getcwd())
        zipfiles_source(local_path)
