# The purpose of the script is to find the GCP storage location of file.  The
# file name must be on a csv in a field called filename

import pandas as pd
import os
import path
import glob
from google.cloud import storage
storage_client = storage.Client()
from datetime import datetime

bucketName = "enter bucketname...."
csv = r"csv....."# csv to read
image_folder = "\\\\bucket_name\\"  #full file name to document in csv
path = r'C:\test' # where you want to save the output csv

source_csv = pd.read_csv(csv, low_memory=False)
def save_csv(output_dict, path):
    """
    Saves the list of roi dictionaries into a .csv file
    Args:
        output_dict (list): a list of ROI dictionaries
        path (PathLike): the location to save the .csv file to

    """

    # Save without index since that clutters the csv and the ROI's will be unique
    df = pd.DataFrame.from_dict(output_dict)
    df.to_csv(path, index=False)

    return df


def get_image_folder_list(directory):
    dict_of_files = {}
    for root, directories, files in os.walk(image_folder, topdown=False):
        for name in files:
            dcmfile = (os.path.join(root, name))
            if dcmfile.endswith(".dcm"):
                full_path = os.path.join(root, name)  # for file in filenames]
                base_name = os.path.basename(full_path)
                dict_of_files[base_name] = full_path
    return dict_of_files


def get_bucket_image_dic(bucketName):
    """List all files in GCP bucket.""" 
    dict_of_files = {}
    bucket = storage_client.get_bucket(bucketName)
    bucketFolder = "bucket sub folder....."
    files = bucket.list_blobs(prefix=bucketFolder)
    fileList = [bucketName +'/'+ file.name for file in files if '.dcm' in file.name]
    for bucket_object in fileList:
        base_name = os.path.basename(bucket_object)
        dict_of_files[base_name] = bucket_object
    
    return dict_of_files


def get_base_name(file_name):
    file = ''.join(str(e) for e in file_name)
    base = os.path.basename(file)
    
    return base

directory_dict = get_bucket_image_dic(bucketName)

for i, row in source_csv.iterrows():
    dicom_file = row["filename"]
    base_name = get_base_name(dicom_file)
    
    try:
        dicom_file_path = directory_dict[base_name]
        if os.path.isfile(dicom_file_path):
            pass
        else:
            print(False)
        
    except Exception as e:
        dicom_file_path = None
    
    source_csv.at[i,'image_GCP_location'] = dicom_file_path
save_csv(source_csv, path + '//' + f"{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}.csv")
    

