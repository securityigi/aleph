#!/usr/bin/env python

import os, sys, logging, shutil
from multiprocessing import Process, Queue
from copy import copy

from features import settings, collectors
from features.components import SampleManager
from features.datastore import es

from features.settings import SAMPLE_STORAGE_DIR, SAMPLE_TEMP_DIR

class AlephServer(object):

    # Properties
    logger = None

    running = False

    sample_managers = []

    collectors = []

    sample_queue = None

    def __init__(self):
        self.init_logger()
        self.sample_queue = Queue()
        self.init_db()
        self.create_directories()
        self.init_sample_managers()
        self.init_collectors()

    def __del__(self):
        self.stop_services()

    def init_db(self):
        try:
            es.setup()
        except Exception, e:
            raise elasticsearch.exceptions.ConnectionError("Unable to connect to elasticsearch database")


    def create_directories(self):

        if not os.path.exists(SAMPLE_STORAGE_DIR):
            try:
                os.mkdir(SAMPLE_STORAGE_DIR)
                self.logger.info("Directory %s created" % SAMPLE_STORAGE_DIR)
            except OSError, e:
                raise OSError("Unable to create sample storage dir at %s: %s" % (SAMPLE_STORAGE_DIR, str(e)))

        try:
            if os.path.exists(SAMPLE_TEMP_DIR):
                shutil.rmtree(SAMPLE_TEMP_DIR)
            os.mkdir(SAMPLE_TEMP_DIR)
            self.logger.info("Directory %s created" % SAMPLE_TEMP_DIR)
        except OSError, e:
            raise OSError("Unable to create sample temporary dir at %s: %s" % (SAMPLE_TEMP_DIR, str(e)))

    def init_logger(self):

        log_level = logging.DEBUG if settings.DEBUG else logging.INFO

        if not os.path.exists(settings.LOGGING['directory']):
            os.makedirs(settings.LOGGING['directory'])

        logging.basicConfig(
            filename=os.path.join(settings.LOGGING['directory'], settings.LOGGING['filename']),
            level=log_level,
            format=settings.LOGGING['format'],
            )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Logger module initialized')

    def stop_services(self):
        for sample_manager in self.sample_managers:
            sample_manager.stop()
        for source, instance in self.collectors:
            if instance is not None and instance.is_alive():
                instance.stop()
        
    def start_services(self):

        self.start_sample_managers()
        self.start_collectors()

    def init_sample_managers(self):

        for i in range(settings.SAMPLE_MANAGERS):
            self.sample_managers.append(self.sample_manager_instance())

    def init_collectors(self):

        self.logger.info('Loading collectors from sources configuration')

        self.collectors = []
        self.sources = copy(settings.SAMPLE_SOURCES)

        for source in self.sources:
            instance = self.collector_instance(source)
            self.collectors.append( ( source, instance ) )

    def start_collectors(self):
        for source, instance in self.collectors:
            instance.start()

    def start_sample_managers(self):
        for manager in self.sample_managers:
            manager.start()

    def sample_manager_instance(self):
        return SampleManager(self.sample_queue)

    def collector_instance(self, source):
        source_type = source[0]
        source_params = source[1]

        if source_type not in collectors.COLLECTOR_MAP:
            raise NotImplementedError('%s collector is not implemented.' % source_type)

        instance = collectors.COLLECTOR_MAP[source_type](source_params, self.sample_queue)
        self.logger.info('Collector "%s" loaded' % (source[0]))
        return instance

    def run(self):
        self.logger.info('Starting AlephServer')
        self.start_services()
        print 'AlephServer started.'
        self.monitor()

    def monitor(self):

        self.running = True
        try:
            while self.running:
                # SampleManager
                for manager in self.sample_managers:
                    if manager and manager.is_alive():
                        manager.join(1.0)
                    else:
                        self.sample_managers.remove(manager)
                        self.sample_managers.append(self.sample_manager_instance())

                # Collectors
                for source, instance in self.collectors:
                    if instance is not None and instance.is_alive():
                        instance.join(1.0)
                    else:
                        instance = self.collector_instance(source)

        except (KeyboardInterrupt, SystemExit):
            self.logger.info('CTRL+C received. Killing all workers')
            print "CTRL+C received. Killing all workers"
            self.running = False
            self.stop_services()
