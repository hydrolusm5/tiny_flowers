import logging
import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pathtools
import numpy as np
import pydicom
from PIL import Image
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence



log = logging.getLogger(__name__)


def convert_array_to_dcm_slice(
    slice_number,
    pixel_data,
    BitsAllocated,
    StudyInstanceUID,
    SeriesInstanceUID,
    uid_prefix,
    PixelSpacing,
    SeriesDescription,
    output_dir,
    basename,
):
    """
    Creates a DICOM file from a two-dimensional array.

    BitsAllocated must match the datatype of the pixel_data. The pixel_data can only be
    uint8 or uint16 to be viewed by the OHIF Viewer.

    Args:
        slice_number (integer): Index of the 3D array pixel_data is selected from
        pixel_data (numpy.Array): Array of values representing pixels
        BitsAllocated (integer): Bits allocted for each pixel
        StudyInstanceUID (string): UID of this study
        SeriesInstanceUID (string): UID of this series
        DimensionOrganizationUID (string): UID to identify dimensions are used across
            all DICOM files of this series
        uid_prefix (string): A uid prefix for ending at preselected section
        PixelSpacing (list): A list of two floats denoting pixel spacing
        SeriesDescription (string): The series description
        output_dir (string): The directory to output each dicom
    """
    dcm_filename = f"{output_dir}/{basename}.dcm"
    SOPInstanceUID = pydicom.uid.generate_uid(prefix=uid_prefix)
    # Coded version of DICOM file '0004cfab-14fd-4e49-80ba-63a80b6bddd6.dcm'
    # Produced by pydicom codify utility script

    # Main data elements
    ds = Dataset()
    ds.SpecificCharacterSet = "ISO_IR 100"
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
    ds.SOPInstanceUID = SOPInstanceUID
    ds.ContentDate = datetime.today().strftime("%Y%m%d")
    ds.ContentTime = datetime.today().strftime("%H%M%S")
    ds.AccessionNumber = ""
    ds.Modality = "CR"
    ds.ConversionType = "WSD"
    ds.SeriesDescription = SeriesDescription
    ds.StudyInstanceUID = StudyInstanceUID
    ds.SeriesInstanceUID = SeriesInstanceUID
    ds.InstanceNumber = str(slice_number + 1)
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid(prefix=uid_prefix)
    ds.ReferringPhysicianName = ""
    ds.PatientName = SeriesDescription
    ds.PatientID = SeriesDescription
    ds.PatientBirthDate = ""
    ds.PatientSex = "U"
    ds.PatientAge = "0"
    ds.StudyInstanceUID = StudyInstanceUID
    ds.SeriesInstanceUID = SeriesInstanceUID
    ds.StudyID = ""
    ds.SeriesNumber = "1"
    ds.InstanceNumber = str(slice_number + 1)
    ds.PatientOrientation = ""
    if len(pixel_data.shape) < 3:
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
    elif pixel_data.shape[2] == 3:
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"

    ds.Rows = pixel_data.shape[0]
    ds.Columns = pixel_data.shape[1]

    ds.PixelSpacing = PixelSpacing
    ds.BitsAllocated = BitsAllocated
    ds.BitsStored = BitsAllocated
    ds.HighBit = BitsAllocated - 1
    ds.PixelRepresentation = 0
    ds.LossyImageCompression = "01"
    ds.LossyImageCompressionMethod = "ISO_10918_1"
    ds.PixelData = pixel_data.tobytes()

    ds.is_implicit_VR = False
    ds.is_little_endian = True

    # Check Marks (✓) indicate these tags were addressed above
    # Down Arrows (↓) indicate these tags are addressed below

    # OHIF Viewer Requirements
    """
        (0020,000E) UI SeriesInstanceUID ✓
        (0020,000D) UI StudyInstanceUID ✓
        (0008,0060) CS Modality ✓
        (0008,0201) SH Timezone Offset from UTC ↓
        (0008,103E) LO Series Description ✓
        (0008,1190) UI RetrieveURL ↓
        (0020,0011) IS SeriesNumber ↓
        (0020,1209) IS NumberOfSeriesRelatedInstances ↓
        (0040,0244) DA PerformedProcedureStepStartDate ↓
        (0040,0245) TM PerformedProcedureStepStartTime ↓
        (0040,0275) SQ RequestAttributesSequence ↓
        (0040,0009) SH ScheduledProcedureStepID ↓
        (0040,1001) SH RequestedProcedureID ↓
    """
    ds.TimezoneOffsetFromUTC = "-0600"
    ds.StudyDate = ds.ContentDate
    ds.StudyTime = ds.ContentTime
    ds.SeriesNumber = "1"
    ds.NumberOfSeriesRelatedInstances = "1"
    ds.PerformedProcedureStepStartDate = ds.ContentDate
    ds.PerformedProcedureStepStartTime = ds.ContentTime
    ds.RequestAttributesSequence = Sequence()
    ds.ScheduledProcedureStepID = "1"
    ds.RequestedProcedureID = "1"

    # DICOM MR Classifier Requirements
    """
        (0008,0060) CS Modality ✓
        (0008,103E)	LO SeriesDescription ✓
        (0020,000D)	UI StudyInstanceUID ✓
        (0020,0010)	SH StudyID ↓
        (7FE0,0010) OB or OW Pixel Data ✓
        (0008,0070)	LO Manufacturer ↓
    """
    ds.StudyID = "1"
    ds.Manufacturer = "Imidex"

    # FileMetaDataset stuff is important... somehow:
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = "1.2.840.10008.1.2.1"
    # Save single DICOM file
    ds.save_as(dcm_filename, write_like_original=False)


def convert_image_to_dicom(input_filename, work_dir, basename):
    """
    Convert provided image to dicom archive.

    Args:
        input_filename (Pathlike): Path to input PerkinElmer Nuance (im3) file.
        work_dir (Pathlike): The working directory to save DICOM slices in

    Returns:
        Pathlike: Path to archive of dicom slices produced
    """
    # Prepare named output directory under the working directory
    input_filepath = Path(input_filename)
    output_dir = Path(work_dir) #/ sanitize_filename(input_filepath.stem)
    os.makedirs(output_dir, exist_ok=True)

    # Load the image file into a numpy array
    image_ptr = Image.open(input_filepath)

    # See PIL.Image modes:
    # https://pillow.readthedocs.io/en/3.0.x/handbook/concepts.html#modes
    # Convert to "RGB" if not already there.
    if image_ptr.mode in ["RGBA", "CMYK", "LAB", "YCbCr", "HSV"]:
        image_ptr = image_ptr.convert(mode="RGB")

    # The OHIF Viewer does not yet display color dicoms
    # So, Squash them all to grayscale for now:
    image_ptr = image_ptr.convert(mode="L")

    image_array = np.array(image_ptr)
    # modes L, P, RGB, RGBA, CMYK, YCbCr, LAB, and HSV are all 8-bit
    # May need work to accomodate other image types.
    BitsAllocated = 8

    # Collate DICOM tags that will be shared across slices.
    StudyInstanceUID = pydicom.uid.generate_uid()
    uid_prefix = StudyInstanceUID[: StudyInstanceUID.replace(".", ":", 7).find(".") + 1]
    SeriesInstanceUID = pydicom.uid.generate_uid(prefix=uid_prefix)

    PixelSpacing = [1, 1]
    SeriesDescription = output_dir.name
    convert_array_to_dcm_slice(
        1,
        image_array,
        BitsAllocated,
        StudyInstanceUID,
        SeriesInstanceUID,
        uid_prefix,
        PixelSpacing,
        SeriesDescription,
        output_dir,
        basename,
    )
    # TODO: 
    #output_filename = str(output_dir) + ".dicom.zip"
    #cwd = os.getcwd()
    #os.chdir(work_dir)
    #zip_file = ZipFile(output_filename, "w")
    #for root, _, files in os.walk(SeriesDescription):
        #for fl in files:
            #zip_file.write(os.path.join(root, fl))
    #os.chdir(cwd)
    #return output_filename
