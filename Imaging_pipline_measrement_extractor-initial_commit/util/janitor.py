import os
from common.custom_expression import NoConfigFileException
from common.constants import ConfigFile, FileTypes
from path import Path


class TheJanitorAtWork:
    """
    Helper class for performing config and OS related task
    """

    def __init__(self):
        """
        Constructor for the "Janitor"
        :param: None
        """
        self.working_dir = os.getcwd()

    def get_config_file(self):
        """
        get the config file location and check if it exist
        :return: config file path
        """
        # get the path of config file
        script_dir = Path(self.working_dir)
        config_child_path = ConfigFile.CONFIG.value
        config_file_full_path = (str(script_dir) + '\\' + str(config_child_path))

        # confirm that the path exist
        if os.path.exists(config_file_full_path):
            print("config file found....")
            print(f"config file located {config_file_full_path}")

        else:
            # raise an error if the config file isn't in the config directory
            print("Measurement extractor is exiting....")
            raise NoConfigFileException("Config file is not in the common folder......")

        return config_file_full_path

    def clean_up_working_dir(self):
        """
        Method to remove old files
        :return: None
        """

        # get a list of old files
        list_files = []
        for root, directories, files in os.walk(self.working_dir, topdown=False):
            for name in files:
                logfile = (os.path.join(root, name))
                if logfile.endswith(FileTypes.LOG.value):
                    list_files += [os.path.join(root, name)]
        # remove old log files
        for file in list_files:
            os.remove(file)


    def get_list_patient_ids(self):
        """
        :return: list_of_csv a list of CSVs containing MRNs and study dates
        """
        list_of_csv = []
        # check the current dir for CSVs
        current_folder_list = os.listdir(self.working_dir)
        for file in current_folder_list:
            file_full_path = os.path.join(self.working_dir, file)
            if file_full_path.endswith(FileTypes.CSV.value):
                list_of_csv += [file_full_path]

        return list_of_csv

    @staticmethod
    def final_concat_list_of_patient_ids(list_of_csv, patient_list_source):
        """
        merge all CSVs to one file
        check that the CSV has the mandatory headers
        :param list_of_csv:
        :param patient_list_source:
        :return: data frame of patient MRN and study dates, success or failure
        """

        final_file = pd.concat(map(pd.read_csv, list_of_csv), ignore_index=True)

        source_file_columns = final_file.columns.str.lower()
        if all(value in patient_list_source.src_columns for value in source_file_columns):
            results = True
        else:
            results = False

        return results, final_file