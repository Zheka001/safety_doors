# -*- coding: utf-8 -*-
from flask_cors import CORS
from flask_script import Manager, Server, Command

from src.web import create_flask_application
from src.utils.config import SingleConfig
from src.assessment.label_creator import LabelCreator
from src.ml.classifier import Classifier
from src.ml.data_processor import DataProcessor


def get_manager():
    config = SingleConfig()
    application = create_flask_application(config)
    CORS(application, resources={r'/*': {'origins': config.flask.ORIGINS}}, supports_credentials=True)
    url_without_protocol = config.flask.ORIGINS[0].split('/')[-1]
    if ':' in url_without_protocol:  # todo: переделать
        host, port = url_without_protocol.split(':')[0], 5000
    else:
        host, port = url_without_protocol, None
    manager = Manager(application)
    manager.add_command('app', Server(host=host, port=port))
    manager.add_command('label', Command(LabelCreator.run))
    manager.add_command('train', Command(Classifier.run))
    manager.add_command('predict', Command(DataProcessor.run))
    return manager


if __name__ == "__main__":
    get_manager().run()
