import os
from zipfile import ZipFile

def get_list_directories(path):
    directories = [x[1] for x in os.walk(path)]

    return directories[0] 

def download(id_project):
    directories = get_list_directories("images")

    dirname = ""

    for i in directories:
        name = i.split(" ")
        if name[0] == str(id_project):
            dirname = i
            break

    zip_obj = ZipFile("images/zip/" + dirname + '.zip', 'w')

    for folderName, subfolders, filenames in os.walk("images/" + dirname):
        for filename in filenames:
           filePath = os.path.join(folderName, filename)
           zip_obj.write(filePath)

    zip_obj.close()

    return dirname + '.zip'