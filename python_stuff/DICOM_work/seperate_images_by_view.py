
import datetime
from datetime import datetime
import time
from csv import reader
from pydicom import dcmread
from pydicom.uid import generate_uid
import os
from os import path
import logging
import datetime
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
import os
from pathlib import Path
import shutil, errno


subject_total = 0
AP = 'AP'
PA = 'PA'
UN = 'unknown'
PA_list = 0
AP_list = 0
UN_list = 0
total_dcm = 0
DCM = '.dcm'
csv_read = r"C:\temp\read\mimic_p10.csv"
report_dir = 'C:\\archive\\MIMIC\\report\\DICOM\p10\p10'


def get_filename_datetime():
    # Use current date to get a text file name.
    now = datetime.now()
    dt_string = now.strftime("%m_%d_%Y_%H_%M_%S")
    return "logfile_" + dt_string + ".txt"


# Get full path for writing.
name = get_filename_datetime()
path = "C:\\temp\\log_files\\" + name

# open log file
if not os.path.isfile(path):
    log = open(path, "w")
    log.close

if os.path.isfile(path):
    logging.basicConfig(filename=path, filemode='w', level=logging.DEBUG)
    logging.info(f'log file sucessfully created!')
    logging.info(f"{csv_read}")

else:
    # exit the program if log file wasn't created
    print(f'Unable to create log file! Exiting')
    quit(0)


def view_position(dcmfile):
    ds = dcmread(dcmfile)
    try:
        viewposition = " "
        # check view position
        elemVP = ds[0x0018, 0x5101]
        viewposition = elemVP.value
        logging.warning(f"{dcmfile}The view position is {viewposition}")
    except:
        viewposition = "none"
    if len(viewposition) == 0:
        viewposition = "unknown"
    return viewposition


def get_cell_value(cell):
    acc_number_pre = (cell.value)
    temp = acc_number_pre.replace(r'/', '\\')
    temp1 = temp.replace('files', '')
    acc_number = os.path.splitext(temp1)[0]
    pre_path = (r'C:\archive\MIMIC\DCM')
    full_path = (pre_path + acc_number)
    return full_path


def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise


def copysomething(src, dst):
    if os.path.isfile(src):
        try:
            shutil.copy(src, dst)
            logging.info(f"{src} was copied to {dst}")
        except OSError as exc:  # python >2.5
            os.makedirs(dst)
            shutil.copy(src, dst)
    else:
        logging.warning(f"{src} doesnt exsist")


def make_dir(dir):
    if not os.path.exists(dst):
        logging.warning(f"{dir}does not exist")

        try:
            os.makedirs(dst)
        except:
            logging.warning(f"unable to create dir [dir]")


startTime = time.time()


for root, directories, files in os.walk(directory, topdown=False):
    for name in files:
        dcmfile = (os.path.join(root, name))
        split =  os.path.splitext(dcmfile)
        dcmfile_ext = split[1]
        if dcmfile_ext == dcm:
            print(dcmfile)        
            total += 1
            ds = dcmread(dcmfile)


            for dcm_file in list_dcm_Files:
                if dcm_file.endswith(DCM):
                    total_dcm = total_dcm + 1
                    vp = view_position(dcm_file)
                    print(vp)
                    dcm_file_s = dcm_file.split("\\")
                    subject_num = dcm_file_s[5]
                    acc_num = dcm_file_s[6]
                    base = os.path.join(subject_num, acc_num)
                    logging.info(f"The file is {dcm_file}")

                    if vp == AP:
                        print(f'View position is AP')
                        logging.info(f"View position is {vp}")
                        AP_list = AP_list + 1
                        pre_path_AP = (r"C:\archive\MIMIC\DCM_curate\p10\AP_only")
                        dst = os.path.join(pre_path_AP, base)
                        logging.info(f"The view position is {vp}")
                        logging.info(f"The file will be copied to {dst}")
                        make_dir(dst)
                        report_dcm = os.path.join(report_dir, subject_num, acc_num + ".dcm")
                        copysomething(dcm_file, dst)
                        copysomething(report_dcm, dst)

                    if vp == PA:
                        print(f"View position is {vp}")
                        PA_list = PA_list + 1
                        pre_path_PA = (r"C:\archive\MIMIC\DCM_curate\p10\PA_only")
                        dst = os.path.join(pre_path_PA, base)
                        logging.info(f"The view position is {vp}")
                        logging.info(f"The file will be copied to {dst}")
                        report_dcm = os.path.join(report_dir, subject_num, acc_num + ".dcm")
                        make_dir(dst)
                        copysomething(dcm_file, dst)
                        copysomething(report_dcm, dst)

                    if vp == UN:
                        print(f'View position is {vp}')
                        logging.info(f"View position is {vp}")
                        UN_list = UN_list + 1
                        pre_path_unknown = (r"C:\archive\MIMIC\DCM_curate\p10\unknown_only")
                        dst = os.path.join(pre_path_unknown, base)
                        logging.info(f"The view position is {vp}")
                        logging.info(f"The file will be copied to {dst}")
                        make_dir(dst)
                        report_dcm = os.path.join(report_dir, subject_num, acc_num + ".dcm")
                        copysomething(dcm_file, dst)
                        copysomething(report_dcm, dst)
                    logging.info("==========================")


        else:
            logging.warning(r'{path} is not real')
logging.info("==========================")
logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>")
logging.info("\n")
executionTime = (time.time() - startTime)
logging.info(f'It took {executionTime} to process:')
logging.info("\t"f'The total dcm file: {total_dcm}')
logging.info("\t"f'The total PA: {PA_list}')
logging.info("\t"f'The total AP: {AP_list}')
logging.info("\t"f'The total Unknown: {UN_list}')
logging.info("\t"f'The total subjects: {subject_total}')


