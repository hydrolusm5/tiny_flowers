import csv
import os
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence
import pydicom
import datetime
from datetime import datetime
import time
import os
import logging
# from util import convert_array_to_dcm_slice
# from util import convert_image_to_dicom
from PIL import Image, ImageFont, ImageDraw
import textwrap
import shutil
from pydicom import dcmread
from colorama import Fore

filename = r'file......'


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
    logging.info(f"{filename}")

else:
    # exit the program if log file wasn't created
    print(f'Unable to create log file! Exiting')
    quit(0)


def destination_folder(adjudication_number, subject_num, study_num):
    '''
    create directory: c:\archive\BIMCV\adjudication_number\subject_ID\study_ID

    :param
        adjudication_number: a string value representing the organization number representation (1-9)
        subject_num: a string value representing the image's subject number
        study_num: a string value representing the image's study number
    :return
        a path like string value
    '''
    root = 'y:\\image_set\\upload\\'

    dest = os.path.join(root, adjudication_number, subject_num, study_num)
    folder_exist = os.path.isdir(dest)
    if not folder_exist:
        os.makedirs(dest)
        print('make it')
    else:
        print(f'{dest} already exist')
    print(dest)

    return dest


class ImageAttributes:

    def __init__(self, line):
        """"
        Parse the project's metadata containing csv

        :param
            line: a string a interation of a dataframe row

        :returns
            string value of the row's cells
        """

        # self.image_location = line['image_path'] + adjudication_num_fc # location of the image
        self.DCM_base = line['ImageID_dicom']
        self.subject_num = line['NEW_PATIENT_ID']  # This will be the subject number
        self.study_date = line['StudyDate_DICOM']  # This will be the study date number
        self.report_verbage = line['report_translated_english']  # This will be the report statement
        self.view_position = line['Projection']  # This will be the view position
        self.manufacture = line['Manufacturer_DICOM']  # manufactuer

        adjudication_num_string = line['adjudication_batch']
        adjudication_num_fc = adjudication_num_string[0]

        if adjudication_num_fc == 'n':
            self.adjudication_num = str(9)
        else:
            self.adjudication_num = adjudication_num_fc
        self.pt_dob = line['PatientBirth']
        self.PixelAspectRatio = line['PixelAspectRatio_DICOM']
        self.WindowWidth = line['WindowWidth_DICOM']
        self.Exposure = line['Exposure_DICOM']
        self.PatientSex = line['PatientSex_DICOM']
        self.SpatialResolution = line['SpatialResolution_DICOM']
        self.ExposureTime = line['ExposureTime']
        self.ExposureInuAs = line['ExposureInuAs_DICOM']
        self.XRayTubeCurrent = line['XRayTubeCurrent_DICOM']
        self.RelativeXRayExposure = line['RelativeXRayExposure_DICOM']
        self.PhotometricInterpretation = line['PhotometricInterpretation_DICOM']
        self.study_num = line['ReportID']  # this will be the study number


def copysomething(src, dst):
    """Copy a file from its source to a specified location
    :param
        src: a path-like string for the source file location
    :param
        dst: a path-like string for the source file destination
    :return:
        nothing
    """
    if os.path.isfile(src):
        try:
            shutil.copy(src, dst)
            # logging.info(f"{src} was copied to {dst}")
        except OSError as exc:  # python >2.5
            os.makedirs(dst)
            shutil.copy(src, dst)
    else:
        print(f"{src} doesnt exsist")


def dicom_header_add(
        dcm_file,
        vp,
        manufacture,
        dob,
        exposure,
        sex,
        resolution,
        exposure_time_milliamps,
        tube_current,
        relative_exposure,
        photometric,
        subject_num
):
    '''
    Add/change the following dicom fields:

        view_position = line['Projection'] # This will be the view position
        manufacture = line['Manufacturer_DICOM'] # manufactuer
        pt_dob = line['PatientBirth']
        PixelAspectRatio = line['PixelAspectRatio_DICOM']
        WindowWidth = line['WindowWidth_DICOM']
        Exposure = line['Exposure_DICOM']
        PatientSex = line['PatientSex_DICOM']
        SpatialResolution = line['SpatialResolution_DICOM']
        ExposureTime = line['ExposureTime']
        ExposureInuAs = line['ExposureInuAs_DICOM']
        XRayTubeCurrent = line['XRayTubeCurrent_DICOM']
        RelativeXRayExposure = line['RelativeXRayExposure_DICOM']
        PhotometricInterpretation = line['PhotometricInterpretation_DICOM']

    Args:
        Each of the above dicom attributes


    '''
    if tube_current == "None":
        tube_current = 0

    tube_current = int(tube_current)
    exposure_time_milliamps = float(exposure_time_milliamps)

    print(f'file name is {dcm_file}')
    print(f' view position is {vp}')
    print(f' maker is {manufacture}')
    print(f' exposure is {exposure}')
    print(f' sex is {sex}')
    print(f' resolution is {resolution}')
    print(f' exposure time is {exposure_time_milliamps}')
    print(f' tube current is {tube_current}')
    print(f' relative exposure is {relative_exposure}')
    print(f' photmetric is {photometric}')
    print(f'{subject_num}')
    ds = dcmread(dcm_file)
    dicom_elements = ["ds.ViewPosition = vp", "ds.PatientBirthDate = dob",
                      "ds.Exposure = exposure", "ds.PatientSex = sex", "ds.SpatialResolution = resolution",
                      "ds.ExposureTimeInms = exposure_time_milliamps", "ds.XRayTubeCurrent = tube_current",
                      "ds.RelativeXRayExposure = relative_exposure", "ds.PhotometricInterpretation = photometric",
                      "ds.PatientName = subject_num", "ds.PatientID = subject_num",
                      "ds.Manufacturer = manufacture"]

    for element in dicom_elements:

        try:
            element
            ds.save_as(dcm_file, write_like_original=False)
            print('Tags changed')
        except Exception as e:

            print(Fore.RED + f'{dcm_file} {e}')


def create_report(report, subject_number, study_number, pt_sex, pt_dob, study_date, dest):
    '''
    Generates a report according to the subject number

    args:
        inputs the subject number, study number, and patient sex
    output:
        a jpg report of the subject saved in the subject's folder
        returns the location of the jpeg file

    '''
    # creating a image object
    image = Image.open(r'C:\temp\read\valencia_background.jpg')

    draw = ImageDraw.Draw(image)

    # specified font size
    font = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', 50)
    spacing = 50

    # Wrap the report text.
    value = report
    wrapper = textwrap.TextWrapper(width=100)
    string = wrapper.fill(text=value)

    # drawing subject ID
    subject_line = f'Subject Number: {subject_number}'
    draw.text((0, 450), subject_line, fill="black",
              font=font, spacing=spacing, align="left")

    # drawing study ID
    study_line = f'Study Number: {study_number}'
    draw.text((0, 510), study_line, fill="black",
              font=font, spacing=spacing, align="left")

    # drawing sex
    sex_line = f'Subject Sex: {pt_sex}'
    draw.text((0, 570), sex_line, fill="black",
              font=font, spacing=spacing, align="left")

    # drawing dob
    dob_line = f'Subject DOB: {pt_dob}'
    draw.text((0, 630), dob_line, fill="black",
              font=font, spacing=spacing, align="left")

    # drawing study date
    study_date_line = f'Study_date: {study_date}'
    draw.text((0, 690), study_date_line, fill="black",
              font=font, spacing=spacing, align="left")

    # drawing report
    draw.text((100, 850), ">===Report===>", fill="black",
              font=font, spacing=spacing, align="left")
    draw.text((100, 950), string, fill="black",
              font=font, spacing=spacing, align="left")

    report_destination_jpeg = os.path.join(dest + '\\' + "report_" + study_number + ".jpg")
    print(report_destination_jpeg)
    image.save(report_destination_jpeg)
    # image.show()

    return report_destination_jpeg


def tag_the_report(report_dcm):
    """
    change the view position in the report dataset header to report.
    This is used to tag these images as reports in flywheel

    args:
        The dcm file
    """
    report = "FinalReport"

    try:
        ds = dcmread(report_dcm)
        ds.ViewPosition = report
        ds.save_as(report_dcm, write_like_original=False)
        print('The report is now labeled {ds.ViewPosition}')

    except Exception as e:
        print(f'{report_dcm} is unreadable')


def assign_uids(folder_path):
    """
    This will assign all dcm files within the the parent study folder the same study UID.
    The reason for this step is to ensure all images with the same subject

    args:
        path of subject-walk from the subject folder to change to UID for all child dcms

    """

    root = 'y:\\Valencia_Adj_only\\upload\\'
    dcm = ".dcm"

    StudyInstanceUID = pydicom.uid.generate_uid()
    folder_exist = os.path.isdir(folder_path)

    if not folder_exist:
        print(f'Can NOT chnage UIDs {folder_path} does NOT exist!!!')
    else:
        for root, directories, files in os.walk(folder_path, topdown=True):
            for name in files:
                dcmfile = (os.path.join(root, name))
                split = os.path.splitext(dcmfile)
                dcmfile_ext = split[1]
                if dcmfile_ext == dcm:
                    print(dcmfile)

                    try:
                        ds = dcmread(dcmfile)
                        try:
                            old_study_uid = ds.StudyInstanceUID
                            print(f'The old uid for {dcmfile} was {old_study_uid}')
                            ds.StudyInstanceUID = StudyInstanceUID
                            print(f'The new uid for {dcmfile} is {ds.StudyInstanceUID}')
                            ds.save_as(dcmfile, write_like_original=False)

                        except KeyError:

                            print(f'{dcmfile} has no orginal UID!!!')

                    except Exception as e:
                        print(f'{dcmfile} {e}')


d = dict()

if __name__ == "__main__":
    with open(filename, 'r') as data:
        x = 0
        for line in csv.DictReader(data):
            drive_dcm = "y:\\Valencia_Adj_only\\"
            i = ImageAttributes(line)  # 1
            destination = destination_folder(i.adjudication_num, i.subject_num, i.study_num)  # 2
            # src_png_image_location = i.image_location
            src_dicom_image_location = drive_dcm + i.adjudication_num + "\\" + i.subject_num + "\\" + i.study_num + "\\" + i.DCM_base
            print(f'dicom is located here: {src_dicom_image_location}')
            print(f'final destination is here: {destination}')

            # 4 need to add the true value (ie i.image_location)
            dicom_header_add(
                src_dicom_image_location,
                i.view_position,
                i.manufacture,
                i.pt_dob,
                i.Exposure,
                i.PatientSex,
                i.SpatialResolution,
                i.ExposureInuAs,
                i.XRayTubeCurrent,
                i.RelativeXRayExposure,
                i.PhotometricInterpretation,
                i.subject_num,
            )

            # create dic for VP
            d[src_dicom_image_location] = i.view_position
            # 3
            copysomething(src_dicom_image_location, destination)

            # create the radiology report as a jpeg and save its location
            report_destination = create_report(i.report_verbage, i.subject_num, i.study_num, i.PatientSex, i.pt_dob, i.study_date, destination)

            test = os.path.isfile(report_destination)
            if test:
                print("YEAAAAA BOYYYYYY")

            else:
                print("dope sound")

            # create inputs to be used for the report jpeg to dicom conversion
            newdirpath = (os.path.dirname(report_destination))
            prebasename = (os.path.basename(report_destination))
            basename = (os.path.splitext(prebasename)[0])

            # convert the jpeg report to dicom
            report_dicom = f"{newdirpath}/{basename}.dcm"
            convert_image_to_dicom(report_destination, newdirpath, basename)
            print(f'The report is here: {report_dicom}')

            # tag the report
            tag_the_report(report_dicom)

            # assign UIDS
            assign_uids(destination)
            print('=================================')

            x += 1
            if x > 6159:
                break

    dcm = ".dcm"
    folder_path = r'Y:\Valencia_Adj_only\upload'
    dcm_list = list()
    for root, directories, files in os.walk(folder_path, topdown=True):
        for name in files:
            dcmfile = (os.path.join(root, name))
            split = os.path.splitext(dcmfile)
            dcmfile_ext = split[1]
            if dcmfile_ext == dcm:
                file = dcmfile
                dcm_list.append(file)
