import yaml
from util.xml_transformer import XmlParser
from util.janitor import TheJanitorAtWork
import logging
import logging.config
from util.s3 import S3BucketConnector
from util.xml_transformer import XmlConfig, XmlEtl
from util.csv_transformer import CsvMeasurementFileTargetConfig, CsvEtl
from util.local_storage import LocalStorage
from util.merge_operations import FinalTargetConfig, TheMerger


def main():
    """
    main runtime for measurement extractor
    :return: run status
    """
    # get the config file
    cleanup = TheJanitorAtWork()
    config_file = yaml.safe_load(open(cleanup.get_config_file()))

    # Configure logging
    log_config = config_file['logging']
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(__name__)
    logger.info('Config file found....')

    # get s3 args
    s3_config = config_file['s3']
    s3_bucket_trg = S3BucketConnector(access_key=s3_config['access_key'],
                                      secret_key=s3_config['secret_key'],
                                      endpoint_url=s3_config['trg_endpoint_url'],
                                      bucket=s3_config['trg_bucket'])

    s3_bucket_src = S3BucketConnector(access_key=s3_config['access_key'],
                                      secret_key=s3_config['secret_key'],
                                      endpoint_url=s3_config['trg_endpoint_url'],
                                      bucket=s3_config['src_bucket'])

    s3_bucket_final = S3BucketConnector(access_key=s3_config['access_key'],
                                      secret_key=s3_config['secret_key'],
                                      endpoint_url=s3_config['trg_endpoint_url'],
                                      bucket=s3_config['final_product_bucket'])

    # get xml args
    xml_args = XmlConfig(**config_file['source_xml'])

    # get cvs args
    cvs_args = CsvMeasurementFileTargetConfig(**config_file['source_csv'])

    # get the final file's arguments
    final_file_target_args = FinalTargetConfig(**config_file['final_target_csv'])

    # get local storage object
    ls = LocalStorage()

    """ <---XML Run---> """
    xml_run = XmlEtl(ls, config_file, s3_bucket_src, s3_bucket_trg, xml_args)
    xml_run.etl()

    """ <---CSV Run---> """
    # ' local', 's3_bucket_src', 's3_bucket_trg', and 'src_args'

    csv_run = CsvEtl(ls, s3_bucket_src, s3_bucket_trg,cvs_args)
    csv_run.etl()

    """<---Final product pass--->"""
    # initialize the merger class
    measure_file = TheMerger(final_file_target_args, s3_bucket_final)
    # join xml and csv files
    (merge_df, raw_output) = measure_file.soft_merge()
    # save the raw join
    measure_file.save_raw(raw_output)
    # clean data
    clean_df = measure_file.clean_up(merge_df)
    # rename headers tp desired state
    final_output = measure_file.rename_columns_final(clean_df)
    # save locally
    measure_file.load_local(final_output)


if __name__ == '__main__':
    main()
