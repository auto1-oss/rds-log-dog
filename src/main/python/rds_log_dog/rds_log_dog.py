from __future__ import print_function, absolute_import, division

import logging

from . import __version__
from rds_log_dog.discoverer import Discoverer
from rds_log_dog.log_file_handler import LogFileHandler
from rds_log_dog.s3_utils import setup_s3_destination


class RDSLogDog(object):  # pragma: no cover

    def __init__(self, config):
        self.s3_dst_bucket = config.s3_dst_bucket
        self.s3_dst_prefix_for_logs = config.s3_prefix_for_logs

    @staticmethod
    def setup_logger(level='INFO'):
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        # to avoid multiple handlers to be attached to the logger
        # this happens often with lambda
        if not logger.handlers or logger.handlers == []:
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        logger.debug('set loglevel to DEBUG')
        # disable botocore logging in debug level
        logger = logging.getLogger('botocore')
        logger.setLevel(logging.WARN)
        logger = logging.getLogger('s3transfer')
        logger.setLevel(logging.WARN)

    def sync_logfiles(self, logfiles, logfilehandler):
        for logfile in logfiles:
            logging.info('copying \'%s\' (%d) ...', logfile.name, logfile.size)
            logfilehandler.copy(logfile)

    def discover_logfiles_to_copy(self, logfilehandler):
        files_in_s3 = logfilehandler.discover_logfiles_in_s3()
        logging.debug('found %d files in s3://%s/%s',
                      len(files_in_s3),
                      logfilehandler.dst_bucket,
                      logfilehandler.dst_prefix_instance)
        files_in_rds = logfilehandler.discover_logfiles_in_rds()
        logging.debug('found %d files in %s',
                      len(files_in_rds), logfilehandler.rds_instance.name)
        logfiles = logfilehandler.logfiles_to_copy(
            files_in_rds, files_in_s3)
        return logfiles

    def process_instance(self, instance):
        logging.info('processing rds-instance: \'%s\'', instance.name)
        logfilehandler = LogFileHandler(
            instance,
            self.s3_dst_bucket,
            self.s3_dst_prefix_for_logs)
        setup_s3_destination(logfilehandler.dst_bucket,
                             logfilehandler.dst_prefix_instance)
        logfiles_to_copy = self.discover_logfiles_to_copy(logfilehandler)
        logging.info('going to copy %d new logfiles ...', len(logfiles_to_copy))
        self.sync_logfiles(logfiles_to_copy, logfilehandler)
        # write metric / logentry
        logging.info('synced %d files for \'%s\'',
                     len(logfiles_to_copy), instance.name)

    def run(self):
        logging.info('rds-log-dog version: %s', __version__)
        discoverer = Discoverer()
        instances = discoverer.discover()
        logging.info('%d instances discovered.', len(instances))
        for instance in instances:
            self.process_instance(instance)
        return 0
