import os
from datetime import datetime
import pandas as pd
import shutil
import logging
from common.constants import LocalStorageLocation
from common.custom_expression import WrongFormatException
from path import Path


class LocalStorage:
    """
    Class for interacting with local disk
    """

    def __init__(self):
        """
        Constructor for S3BucketConnector

        :param access_key: access key for accessing S3
        :param secret_key: secret key for accessing S3
        :param endpoint_url: endpoint url to S3
        :param bucket: S3 bucket name
        """
        self.metadata_folder = LocalStorageLocation.METADATA.value
        self.processed_folder = LocalStorageLocation.PROCESSED.value
        self.output_folder = LocalStorageLocation.OUTPUT.value
        self.bad_file_folder = LocalStorageLocation.BAD_FILES.value
        self.incoming_folder = LocalStorageLocation.INCOMING.value
        self.metadata_file = self.metadata_folder +'\\'+ "metadata.csv"
        self.dataframe = pd.read_csv(self.metadata_file, index_col='index')
        self._logger = logging.getLogger(__name__)

    def list_files_in_local_storage(self, file_type):
        """
        listing all files in the local storage

        :param file_type:

        returns:
          files: list of all the file names containing the prefix in the key
        """

        all_files = []
        list_of_files = []
        for (dirpath, dirnames, filenames) in os.walk(Path(self.incoming_folder)):
            all_files += [os.path.join(dirpath, file) for file in filenames]
        for file in all_files:
            if file.endswith('.' + file_type.lower()):
                file_name_path = file
                list_of_files.append(file_name_path)
        self._logger.info(f'found {len(list_of_files)}')
        self._logger.info('Checking for prior processed files')

        return list_of_files

    def get_final_file_list(self, list_of_files):
        """
        looks to see if a file has already been processed
        If file has been processed, move to processed folder
        :return:
        """
        final_file_list = []
        # get the metadata file
        # load metadate file in dataframe
        # iterate over the list of files and check if its in the metadata file.
        # if it is, that means we already processed the file
        for file in list_of_files:
            prebase_name = os.path.basename(file)
            base_name = (os.path.splitext(prebase_name)[0])
            results = self.dataframe.loc[self.dataframe['file_name'] == prebase_name ]

            # if the file is not in the metadata file, add it and add it to the final list
            if len(results) < 1:
                final_file_list.append(file)
            else:
                self._logger.warning(f" file: {prebase_name} has already been processed")
        if len(final_file_list) < 1:
            self._logger.warning('No new files found')
        else:
            self._logger.info(f'Found {len(final_file_list)} final files')

        return final_file_list

    def move_processed_file(self,xml_file:str):
        """
        Once the xml file has been processed move it to the
        processed directory
        :return:
        """

        self._logger.info("Moving files that have been processed")
        file_name = os.path.basename(xml_file)
        target_dest = self.processed_folder + '\\' + file_name
        try:
            shutil.move(xml_file, target_dest)
            self._logger.info(f"Successfully moved processed files to the processed folder {xml_file}")
        except Exception as error:
            print(error)
            self._logger.critical(f"Unable to move the processed files! {xml_file}")

    def move_bad_file(self,xml_file:str):
        """
        Once the xml file has been processed move it to the
        processed directory
        :return:
        """
        self._logger.info(f"Moving the bad files to the Bad file folder {self.bad_file_folder}")
        file_name = os.path.basename(xml_file)
        target_dest = self.bad_file_folder + '\\' + file_name
        try:
            shutil.move(xml_file, target_dest)
        except Exception as error:
            print(error)
            self._logger.critical(f'Unable to move bad file to the Bad file folder: {xml_file}')

    def write_metadata(self, xml_file:str):
        """
        Adds the file to the processed metadata file
        This is make sure we don't process a file twice
        :return: Nothing
        """
        self._logger.info(f'Updating the metadata file: {xml_file}')
        file_base_name = os.path.basename(xml_file)
        file_type = file_base_name.split('.')[1]
        date_time_now = datetime.now()
        date_time_now = date_time_now.strftime("%m/%d/%Y, %H:%M:%S")

        try:
            patient_name_file = file_base_name.split('_')[0]
        except Exception as error:
            patient_name_file = None
            print(error)

        new_row = {'patient_name': patient_name_file, 'file_name': file_base_name, 'file_location': xml_file,
                   'date_processed': date_time_now, 'file_type': file_type}
        d3 = self.dataframe.append(new_row, ignore_index=True)

        d3.to_csv(self.metadata_file, mode='a', header=False)

    def write_df_to_local(self, data_frame: pd.DataFrame, file_name: str, file_format: str):
        """
        writing a Pandas DataFrame to S3
        supported formats: .csv, .parquet

        :data_frame: Pandas DataFrame that should be written
        :key: target key of the saved file
        :file_format: format of the saved file
        """
        self._logger.info(f"Saving the file locally: {file_name}")
        file_base_name = os.path.basename(file_name)

        if data_frame.empty:
            self._logger.info('The dataframe is empty! No file will be written!')
            return None

        if file_format == LocalStorageLocation.CSV.value:
            output_file = self.output_folder + '\\' + file_base_name[0]
            data_frame.to_csv(output_file + '.csv', index=False)
            self._logger.info('File saved successfully')

            return

        if file_format == LocalStorageLocation.HDF.value:
            data_frame.to_hdf(out_buffer, index=False)

            return

        self._logger.info('The file format %s is not '
        'supported to be written to local', file_format)

        self._logger.critical(f"The file doesn't contain the proper headers: {file_name}")
        raise WrongFormatException
