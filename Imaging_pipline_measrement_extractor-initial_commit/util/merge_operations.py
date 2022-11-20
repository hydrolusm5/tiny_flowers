import sys
import pandas as pd
import logging
from common.constants import LocalStorageLocation
import os
from path import Path
from common.custom_expression import UnknownFileOrginException
from typing import NamedTuple
from util.s3 import S3BucketConnector
from common.custom_expression import WrongSourceHeaderException
from datetime import datetime


class FinalTargetConfig(NamedTuple):
    """
    Class for source configuration data

    src_columns: A list of the target column headers
    src_format: str representation of the file format of the target file
    """
    src_columns: list
    trg_format: str

"""
1) seperate the list of csv according to their source data type
there will be two dataframes, one from data source csv and one from 
data source xml
2) Merge the files based on finding number, date and patient ID
3) Save the merged file and cleanup

Note: the files in the final output folder are not moved and a metadata file is not being used.
This in case, a larger final output file is desired.
"""


class TheMerger:
    """
    Responsible for merge operations and associated functions
    """
    def __init__(self, trg_args: FinalTargetConfig, s3_bucket_trg_final: S3BucketConnector):

        self.metadata_folder = LocalStorageLocation.METADATA.value
        self.processed_folder = LocalStorageLocation.PROCESSED.value
        self.output_folder = LocalStorageLocation.OUTPUT.value
        self.bad_file_folder = LocalStorageLocation.BAD_FILES.value
        self.incoming_folder = LocalStorageLocation.INCOMING.value
        self.final_folder = LocalStorageLocation.FINALPRODUCT.value
        self.metadata_file = self.metadata_folder + '\\' + "metadata.csv"
        self.dataframe = pd.read_csv(self.metadata_file, index_col='index')
        self._logger = logging.getLogger(__name__)
        self.csv = 'csv'
        self.xml = 'xml'
        self.trg_args = trg_args
        self.s3_bucket_trg_final = s3_bucket_trg_final
        self.raw_output = LocalStorageLocation.RAW.value

    def list_processed_files(self, file_type='csv'):
        """
        All processed files are csv but the file name contain
        an identfier if its origin was xml or csv
        :param file_type:
        :return:
        """

        all_files = []
        list_of_files = []
        for (dirpath, dirnames, filenames) in os.walk(Path(self.output_folder)):
            all_files += [os.path.join(dirpath, file) for file in filenames]
        for file in all_files:
            if file.endswith('.' + file_type.lower()):
                file_name_path = file
                list_of_files.append(file_name_path)

        return list_of_files

    def source_seperator(self):
        """

        :return: two list of files 1) Files that came from xml 2) files that came from csv
        """
        from_xml_list_of_files = []
        from_csv_list_of_files = []
        self._logger.info('Finding the source of each processed file')

        for file in self.list_processed_files():
            origin_source = file.split('_')[1]
            if origin_source == self.csv:
                from_csv_list_of_files.append(file)
            elif origin_source == self.xml:
                from_xml_list_of_files.append(file)
            else:
                self._logger.critical(f'File has an unrecognizable: {file}')
                raise UnknownFileOrginException
        return from_xml_list_of_files, from_csv_list_of_files

    def dataframe_generator(self):
        """
        generate two dateframes Files that came from xml 2) files that came from csv
        :return:
        """
        self._logger.info('Generating dataframe from processed XML and CSV files')
        #  get the list of file for each origin type
        (xml_files, csv_files) = self.source_seperator()

        if xml_files or csv_files:

            all_csv = []
            all_xml = []
            # run through the list of files and concat to the dataframe
            for file in xml_files:
                df = pd.read_csv(file)
                all_xml.append(df)
            xml_df = pd.concat(all_xml)

            for file in csv_files:
                df = pd.read_csv(file)
                all_csv.append(df)
            csv_df = pd.concat(all_csv)

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', -1)

            return xml_df, csv_df

        else:
            self._logger.warning('No files to parse...')
            sys.exit(0)

    def soft_merge(self):
        """
        Merge by two values 1) the xml's study_date_measurment
                            study_date_measurement
                            2) the csv's studydate
                            StudyDate
                            1)the xml's finding_number
                            finding_number
                            2) the csv's finding
                            Finding
        :return:
        """
        self._logger.info('Preparing to initiate joining of dataframes')
        self._logger.info('<----------------------------------------------------->')
        df_xml, df_csv = self.dataframe_generator()

        match_results = pd.merge(df_xml, df_csv, left_on=['finding_number', 'study_date_measurement',
                                                   'Patient_ID_on_xml_tag'],
                          right_on=['Finding', 'StudyDate', 'PatientID'], how='left', indicator=True)
        results = match_results.drop(['_merge'], axis=1)
        match_results.drop_duplicates(subset=None, keep='first', inplace=True, ignore_index=False)

        # get some stats on the merge
        match_results_count = match_results.groupby('_merge')['_merge'].count()

        total_need_match = df_xml.shape[0]
        total_matches = (match_results.loc[match_results['_merge'] == 'both']).shape[0]
        unmatched_records = (match_results.loc[match_results['_merge'] != 'both']).shape[0]
        self._logger.info(f'A total of: {total_need_match} records need matching')
        self._logger.info(f'There are a total of: {total_matches} matches')
        self._logger.info(f'Unmatched records {unmatched_records}')

        if total_need_match == total_matches:
            self._logger.info('!!! All matches acquired !!!')
        else:
            missing_match_total = int(total_need_match) - int(total_matches)
            self._logger.critical(f'Theres a total of {missing_match_total} unmatched records')
        self._logger.info('Matching results:')
        self._logger.info(match_results_count)
        self._logger.info('<----------------------------------------------------->')

        return results, match_results

    def clean_up(self, dataframe):
        """
        remove unwanted duplicate headers that came from the csv file,
        since we really only want the 'Img' column values

        :param dataframe: THe final dataframe for the merge function
        :return: a clean final product...
        """
        self._logger.info('Performing final data cleansing')
        try:
            df = dataframe.drop(['PatientID', 'StudyDate', 'Finding', 'Volume', 'Area', 'Shape Compactness',
                'Min', 'Max', 'Mean', 'SDev', 'd1_y',  'd2_y','d1xd2_y', 'Avg.Diameter'], axis=1)

            return df

        except Exception as e:
            print(e)
            self._logger.info('unable to clean dataframe, possibly missing header names')

            return None

    def save_raw(self, dataframe):
        """
        Save the file raw for testing and data analysis
        :return:
        """
        self._logger.info('Saving the raw unfiltered join data.....')
        try:
            save_dir = self.raw_output
            dataframe.to_csv(f"{save_dir}\\_measurement_file_raw_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}.csv",
                             index=False)
            return True

        except Exception as error:
            print(error)
            self._logger.critical('Unable to save the raw unfiltered join data!')

            return False

    def load_local(self, dataframe):
        """
        Save the final file locally in final product folder

        :param dataframe:
        :return:
        """
        self._logger.info("checking to see if the final file contains proper headers")
        if all(value in dataframe.columns for value in self.trg_args.src_columns):
            try:
                save_dir = self.final_folder
                dataframe.to_csv(f"{save_dir}\\measurement_file_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}.csv",
                          index=False)
                return True

            except Exception as error:
                print(error)
                self._logger.critical("Unable to save the final file")
                return False
        else:
            self._logger.critical("The final file has missing headers!")
            raise WrongSourceHeaderException

    def load_s3(self, dataframe):
        """
        Save the final file on a S3 bucket

        :param dataframe: Dataframe to save in s3
        :return:
        """
        target_key = 'None'
        self.s3_bucket_trg_final.write_df_to_s3(dataframe, target_key, self.trg_args.trg_format)
        # Writing to target
        self.s3_bucket_trg_final.write_df_to_s3(dataframe, target_key, self.trg_args.trg_format)
        pass

    def rename_columns_final(self, dataframe):
        """
        Rename the columns to match desired state
        :param dataframe:
        :return:
        """
        self._logger.info("Renaming columns for final output")

        try:
            dataframe.rename(columns={
                'Patient_ID_on_xml_tag': 'patient_id_on_xml_tag', 'Patient_name_on_xml_tag': 'patient_name_on_xml_tag',
                'Patient_name_on_file': 'patient_name_on_file', 'Report_Date': 'report_date', 'd1_x': 'd1', 'd2_x': 'd2',
                'd1xd2_x': 'd1xd2', 'Img': 'img'}, inplace=True)
            self._logger.info('<----------- COMPLETE! ----------->')
            return dataframe

        except Exception as e:
            self._logger.critical('Unable to rename column, returning dataframe as is')
            print(e)
            return dataframe

