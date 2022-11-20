import os.path
from datetime import datetime
import pandas as pd
import logging
import re
import numpy as np
import copy
from common.constants import\
    csv_output_study_level_dict, csv_element_list
from typing import NamedTuple
from util.local_storage import LocalStorage
from util.s3 import S3BucketConnector
from common.constants import LocalStorageLocation
from common.custom_expression import WrongSourceHeaderException


class CsvMeasurementFileTargetConfig(NamedTuple):
    """
    Class for source configuration data

    src_first_extract_date: determines the date for extracting the source
    src_columns: source column names
    src_col_date: column name for date in source
    src_col_isin: column name for isin in source
    src_col_time: column name for time in source
    src_col_start_price: column name for starting price in source
    src_col_min_price: column name for minimum price in source
    src_col_max_price: column name for maximum price in source
    src_col_traded_vol: column name for traded volumne in source
    """
    src_columns: list
    src_col_PatientID: str
    src_col_StudyDate: str
    src_col_Finding: str
    src_col_Img: str
    src_col_Volume: str
    src_col_Shape: str
    src_col_Min: str
    src_col_Max: str
    src_col_Mean: str
    src_col_SDev: str
    src_col_d1: str
    src_col_d2: str
    src_col_d1xd2: str
    src_col_Avg_Diameter: str


class CsvEtl:
    """
    Reads the CSV data, transforms and writes the transformed to target
    """

    def __init__(self, local: LocalStorage, s3_bucket_src: S3BucketConnector,
                 s3_bucket_trg: S3BucketConnector, src_args: CsvMeasurementFileTargetConfig,
                 file_format='csv'):
        """
        Constructor for XetraTransformer

        :param s3_bucket_src: connection to source S3 bucket
        :param s3_bucket_trg: connection to target S3 bucket
        :param meta_key: used as self.meta_key -> key of meta file
        :param src_args: NamedTouple class with source configuration data
        :param trg_args: NamedTouple class with target configuration data
        """
        self.file_format = file_format
        self.local = local
        self.output_folder = LocalStorageLocation.OUTPUT.value
        self._logger = logging.getLogger(__name__)
        self.s3_bucket_src = s3_bucket_src
        self.s3_bucket_trg = s3_bucket_trg
        self.src_args = src_args

    def extract_s3(self):
        """
        Read the source data and concatenates them to one Pandas DataFrame

        :returns:
          data_frame: Pandas DataFrame with the extracted data
        """

        # Go to S3 and get the file
        self._logger.info('Extracting CSVs from S3 source files started...')
        pass

    def extract_local(self):
        """
        Get a list of xml files from the incoming folder
        Cleans list make sure file haven't been previously parsed
        :returns:list of xml files
        """

        # Go to local drive and get the files
        self._logger.info('Extracting CSVs from local source started...')
        pre_list_files = self.local.list_files_in_local_storage(self.file_format)

        # run list of files through the rigor
        final_list = self.local.get_final_file_list(pre_list_files)

        return final_list

    def load_s3(self, data_frame: pd.DataFrame):
        """
        Saves a Pandas DataFrame to the target

        :param data_frame: Pandas DataFrame as Input
        """
        pass

    def load_local(self, df_concat, file_name):
        '''

        :param file_name:
        :param df_concat: a super dataframe of measurements
        from csv etl
        :return:
        '''

        file_base_name = os.path.basename(file_name)
        patient_id = file_base_name.split('_')[0]
        df = pd.DataFrame.from_dict(df_concat)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)

        self._logger.info('Attempting to save CSVs to local folder')
        if all(value in df.columns for value in self.src_args.src_columns):

            try:
                df.to_csv(f"{self.output_folder}\\{patient_id}_csv_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}.csv",
                    index=False)
                self._logger.info('Successfully saved CSVs to local folder')
                return True

            except Exception as error:
                self._logger.critical('Unable to save CSVs to local folder')
                return False

        else:
            self._logger.critical(f'The file: {file_name} has missing header information')
            raise WrongSourceHeaderException

    def transform(self, list_files: list):
        """
        :param The final list_files:

        :return:
        """
        for file in list_files:
            cparser = CsvParser(file)
            # csv parser run
            super_d = cparser.csv_etl()

            # skip files that have n
            if super_d is None:
                self._logger.warning(f'Results from file: {file} are blank')
                self._logger.info(f'Moving file to the bad file folder')
                self.local.move_bad_file(file)

            else:
                # save csv locally
                results = self.load_local(super_d, file)
                # if the file is saved successfully,
                # run metadata process

                if results:
                    self.local.write_metadata(file)
                    self.local.move_processed_file(file)

    def etl(self):
        """
        Single run to process the csv files
        :return:
        """

        csv_files = self.extract_local()
        self.transform(csv_files)


class CsvParser:
    """
    parses one csv at a time
    """
    def __init__(self, csv_file: str):
        """
        :param csv_file:
        :return:
        """

        self.csv_file = csv_file
        self._logger = logging.getLogger(__name__)

    def get_patient_id(self):
        """
        The file name contains the patient's name.
        :param file_name:
        :return: string value of patient's name
        """
        file_base_name = os.path.basename(self.csv_file)
        patient_id = file_base_name.split('_')[0]

        return patient_id

    def find_non_lung_findings(self):
        """
        some file aren't using the lung algorithm and instead
        are using the STAT algorithm. Remove these files
        :return:
        """
        with open(self.csv_file, 'r') as file:
            content = file.read()
            if 'SAT Finding' in content:
                return True
            if 'Lung' not in content:
                return True

    def create_data_frame(self):
        """
        load the dataframe from the csv
        :return: dataframe is proper format
        """

        # the incoming csv files at times arent consistent, sometimes they have an added row
        # called measurment filter. This cause the row count to become 'off'
        # to catch this, we try both skip 7 and skip 7 to see which one the files works with
        self._logger.info(f'Parsing the CSV: {self.csv_file}')

        df = pd.read_csv(self.csv_file, sep=',', skiprows=6, engine='python')
        df = df.replace(np.nan, 'None')
        if 'Name' in df.columns:
            return df

        df = pd.read_csv(self.csv_file, sep=',', skiprows=7, engine='python')
        df = df.replace(np.nan, 'None')
        if 'Name' in df.columns:
            print('Warning...Dataframe is using skiprow 7')
            return df

    def csv_transform(self, df):
        """
        Extract the measurment values from the csv
        :return:
        """

        # get total findings
        total_findings_list = []
        for i, row in df['Name'].items():
            # print(row)
            if 'Finding-' in row:
                total_findings_list.append(row)
        total_findings_count = len((total_findings_list))
        #print(f'There are {total_findings_count} findings')

        # remove the bad columns
        regex_str = 'Unnamed'
        df.drop(df.columns[df.columns.str.contains(regex_str)], axis=1, inplace=True)
        # get finding dates
        columns = df.columns.values
        column_list = columns.tolist()
        column_list.remove('Name')

        # create list of finding start indexes
        start_indexes = []
        for finding in total_findings_list:
            find_findings = df[df['Name'].isin([finding])]
            start_indexes.append(find_findings.index[0])

        # created list of find end index
        start_indexes_adj = copy.deepcopy(start_indexes)
        start_indexes_adj.pop(0)
        end_indexes = []
        for number in start_indexes_adj:
            end_number = number
            end_indexes.append(end_number)
        # get the value for the final_line
        final_line = find_findings = df[df['Name'].isin(['Summary'])]
        final_line = final_line.index[0]
        end_indexes.append(final_line)

        # drop name column
        df.drop(['Name'], axis=1, inplace=True)

        # clean column names
        # some columns have base name + date, this will remove 'base
        # change column names to reflect YYYYMMDD
        df.rename(columns=lambda x: x.split(' ')[0], inplace=True)
        df.columns = pd.to_datetime(df.columns, format='%m/%d/%Y').strftime('%Y%m%d')

        # create a dictionary of the start and finish index per finding
        # add the finding number as key and value will be a list of start index - 1
        find_list_index_dict = {}
        if len(total_findings_list) == len(start_indexes):
            for number in range(len(total_findings_list)):
                finding_label = total_findings_list[number]
                index_start_label = start_indexes[number]
                index_end_label = end_indexes[number]
                find_list_index_dict[finding_label] = [index_start_label, index_end_label]

        list_df = []
        # pull the df chunk by index range
        for find_day in total_findings_list:
            begin = find_list_index_dict[find_day][0]
            end = find_list_index_dict[find_day][1]
            df_chunk = df.iloc[begin:end]
            # print(end)
            # drop bad columns (those ful of Nans)
            df_chunk = df_chunk.mask(df_chunk.eq('None')).dropna(axis=1, thresh=7)

            # iterate over each column
            for column in df_chunk.columns.values:
                output_study_level_dict_org = copy.deepcopy(csv_output_study_level_dict)
                #print(f'The find is {find_day} the column name is {column}')
                # The column name is the study date where the measurement came from
                patient_id = self.get_patient_id()
                output_study_level_dict_org['PatientID'].append(patient_id)
                output_study_level_dict_org['StudyDate'].append(column)
                # The find day is the finding number
                output_study_level_dict_org['Finding'].append(find_day)

                # we now have individual list of elements
                element_list = df_chunk[column].tolist()

                # parse this list
                dict_to_fill = {}
                for item in element_list:
                    item = str(item)

                    if re.search('^d1', item):
                        entry = item.split(':')
                        i = item.split(' ')
                        key1 = i[0]
                        value = entry[1]
                        dict_to_fill[key1] = value


                    # remove the segment number as if is merged with the image number value
                    if re.search('^Se', item):
                        i = item.split(' ')
                        key1 = i[3]
                        value_img = i[4]

                        # the Img key has : that need fixing
                        if key1.find(':'):
                            key_img = key1.rstrip(key1[-1])
                        dict_to_fill[key_img] =value_img
                    else:
                        entry = item.split(':')
                        key = entry[0]
                        key = key.strip()
                        try:
                            value = entry[1]
                        except:
                            value = None

                        # remove units if the exists
                        try:
                            value = value.split('c', 1)[0]
                            value = value.strip()
                        except Exception:
                            pass

                        # remove the percentage of change from the value if they exist
                        try:
                            value = value.split('(', 1)[0]
                            value = value.strip()
                        except Exception:
                            pass

                        dict_to_fill[key] = value
                element_list_final = list(dict_to_fill.keys())

                # we now have individual dictionaries ready to fill the main dictionary

                for item in element_list_final:
                    value = dict_to_fill.get(item, 'None')


                    try:
                        output_study_level_dict_org[item].append(value)
                    except Exception as e:
                        #print(e)
                        pass
                # This is fix files that have missing measurements
                # If the expected measurement has no value, insert None into the dictionary
                for k, v in output_study_level_dict_org.items():

                    if len(v) < 1:
                        #print(f'The Key: {k} The value: {v}')
                        v = 'None'
                        output_study_level_dict_org[k].append(v)

                df_ = pd.DataFrame.from_dict(output_study_level_dict_org)  # , columns=output_study_level_dict_org.keys())
                list_df.append(df_)
        df_concat = pd.concat(list_df)

        return df_concat

    def csv_etl(self):
        """
        run the csv etl job
        :return:
        """
        not_lung = self.find_non_lung_findings()
        if not_lung:
            # skip this file
            self._logger.warning('This file is using SAT algorith or doesnt contain lung, skipping....')
            pass
        else:
            data_frame = self.create_data_frame()
            super_df = self.csv_transform(data_frame)
            return super_df









