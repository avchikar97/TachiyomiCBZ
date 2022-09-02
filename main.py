import argparse
import os
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--tachiyomi-path", help="file path to the Tachiyomi folder")
parser.add_argument("-d", "--delete", help="flag to delete the original chapter folder + images once the .cbz file has been created. Default = no deletions", action="store_true")
parser.add_argument("-t", "--test", help="flag to only print the paths of all the .cbz files to be created but do not create them. Default = create the CBZ", action="store_true")
parser.add_argument("-c", "--clean", help="flag to clean up by deleting any .nomedia files in chapter folders that it comes across. Default = no cleanup", action="store_true")
parser.add_argument("-m", "--merge", help="flag to merge all chapters into a single .cbz file. Default = no merge", action="store_true")
parser.add_argument("-v", "--verbosity", help="level of verbosity [0|1|2|3]. Default = 0 (silent)", default=0)

args = parser.parse_args()
tachiyomi_path = str(args.tachiyomi_path)
isDelete = bool(args.delete)
isTest = bool(args.test)
isCleanup = bool(args.clean)
isMerge = bool(args.merge)
curr_verbosity = int(args.verbosity)
NUMBER_ZIPPED = 0
NUMBER_SKIPPED = 0
NUMBER_FILES_DELETED = 0
NUMBER_FILES_MERGED = 0 #to avoid filename conflicts, the number of files to merge must be kept track of


def VERBOSITY_PRINT(str_verbosity:int, str:str):
    if(str_verbosity <= curr_verbosity):
        print(str)

def cbz_folder(folder_name:str):
    """Function to archive the given folder and delete files as specified by input flags.

    Args:
        folder_name (str): The folder to be archived. It has already been checked for already existing archive files.
    """
    global NUMBER_ZIPPED
    global NUMBER_FILES_DELETED
    global NUMBER_FILES_MERGED

    # Deal with the .nomedia file (-c)
    nomedia_path = os.path.join(os.getcwd(), folder_name, ".nomedia")
    if(isCleanup and os.path.exists(nomedia_path)):
        VERBOSITY_PRINT(2, f"Deleting {str(nomedia_path)}")
        NUMBER_FILES_DELETED += 1
        if(not isTest): # message without deleting if this is a test run
            os.remove(nomedia_path)

    # create cbz of format "folder_name.cbz" and contents of `folder`
    # -t means no cbz is created
    if(not isMerge):
        created_cbz_name = str(os.path.join(os.getcwd(), f"{folder_name}.cbz"))
        VERBOSITY_PRINT(1, f"Creating {created_cbz_name}")
        if(not isTest):
           zip_name = shutil.make_archive(folder_name, 'zip', os.path.join(os.getcwd(), folder_name))
           p = Path(zip_name)
           p.rename(p.with_suffix(".cbz"))
           NUMBER_ZIPPED += 1
    else: # executed when chapters are to be merged, instead of zipping one directory at a time, the directory contents are copied to a working directory to be zipped at the end
        if(not isTest):
            # because filenames will likely collide if we copy the names as they exist in the source dir, the files are named sequentially starting from 0
           files=os.listdir(os.path.join(os.getcwd(),folder_name))
           for fname in files:
            file_extension = Path(os.path.join(os.getcwd(),folder_name,fname)).suffix
            shutil.copy(os.path.join(os.path.join(os.getcwd(),folder_name,fname)),os.path.join(os.getcwd(),"working_merge/",(str(NUMBER_FILES_MERGED)+file_extension)))
            NUMBER_FILES_MERGED +=1




    # clean up image folders if -d
    if(isDelete):
        current_chapter_full_path = os.path.join(os.getcwd(), folder_name)
        VERBOSITY_PRINT(2, f"Deleting {current_chapter_full_path}")
        if(not isTest):
            shutil.rmtree(current_chapter_full_path)
            # NUMBER_FILES_DELETED += N  ##TODO: when you can find out how many files were just deleted in the folder

def cbz_search(curr_dirr_name, folder_list):
    """Recursively searches through the tree starting at
    `curr_dirr_name` for chapter folders (leaves) that can be archived.

    Args:
        curr_dirr_name (str): The current directory that is being searched
        folder_list (list[str|BytesPath]): A list of directories in the current directory (assumes there are no file names in this list)
    """
    global NUMBER_SKIPPED
    VERBOSITY_PRINT(1, f"Entering {curr_dirr_name}")
    os.chdir(curr_dirr_name)

    for folder_name in folder_list:
        can_cbz_folder = True
        directory_list = os.listdir(os.path.join(os.getcwd(), folder_name))
        directory_only_list = []

        for directory in directory_list:
            if os.path.isdir(os.path.join(folder_name, directory)): # it's a directory
                directory_only_list.append(directory)
            else: # it's a file
                exclude_dict = set([".cbz", ".cbr", ".epub", ".rar", ".zip"])
                file_ext = os.path.splitext(directory)[1]

                if file_ext in exclude_dict:
                    can_cbz_folder = False

        if directory_only_list: # the folder being examined has directories in it - it is not a chapter so explore the directories
            cbz_search(folder_name, directory_only_list)
        else: # the folder_name is a chapter that can be CBZd
            # only CBZ the folder if there are no cbz, cbr, epubc, rar, or zip files in there
            if(can_cbz_folder):
                cbz_folder(folder_name)
            else:
                VERBOSITY_PRINT(3, f"Skipping {os.path.join(os.getcwd(), folder_name)} - archive files are already present in this folder")
                NUMBER_SKIPPED += 1

    VERBOSITY_PRINT(1, f"Exiting {os.getcwd()}")
    os.chdir(os.path.dirname(os.getcwd())) # done here leave this folder (could be the comic, could be the source)

if __name__ == "__main__":
    # Start in tachiyomi
    VERBOSITY_PRINT(3, f"tachiyomi_path = {tachiyomi_path}, isDelete = {isDelete}, isTest = {isTest}")

    directory_list = os.listdir(tachiyomi_path)
    directory_list = [directory for directory in directory_list if os.path.isdir(os.path.join(tachiyomi_path, directory))]
    if (isMerge): #this working directory is created after the directory list is genereated, the workind directory will contain all images that will be archived into the final cbz file
        os.mkdir(os.path.join(tachiyomi_path,"working_merge"))
    if directory_list:
        cbz_search(tachiyomi_path, directory_list)
    if (isMerge): #merges all the files in the working directory and deletes the working directory
        zip_name = shutil.make_archive(os.path.join(tachiyomi_path,"merged"), 'zip', os.path.join(tachiyomi_path,"working_merge"))
        p = Path(zip_name)
        p.rename(p.with_suffix(".cbz"))
        NUMBER_ZIPPED += 1
        shutil.rmtree(os.path.join(tachiyomi_path,"working_merge"))
        # os.rmdir(os.path.join(tachiyomi_path,"/working_merge"))
    print()
    print()
    print()
    VERBOSITY_PRINT(0, "RESULT SUMMARY:")
    VERBOSITY_PRINT(0, f"   Number of .cbz files created:                          {NUMBER_ZIPPED}")
    VERBOSITY_PRINT(0, f"   Number of folders skipped (archive already exists):    {NUMBER_SKIPPED}")
    VERBOSITY_PRINT(0, f"   Number of files deleted (not counting page pictures):  {NUMBER_FILES_DELETED}")
    print()
    VERBOSITY_PRINT(0, "PARAMETER INFORMATION:")
    if(isTest):
        VERBOSITY_PRINT(0, "    TEST RUN ONLY - no files were modifed")
    if(isCleanup):
        VERBOSITY_PRINT(0, "    .nomedia files WERE deleted in chapter folders before creating .cbz file")
    else:
        VERBOSITY_PRINT(0, "    .nomedia files WERE NOT deleted in chapter folders before creating .cbz file")
    if(isDelete):
        VERBOSITY_PRINT(0, "    Folders containing the chapter pictures WERE deleted.")
    else:
        VERBOSITY_PRINT(0, "    Folders containing the chapter pictures WERE NOT deleted.")
