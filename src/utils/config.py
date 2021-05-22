# -*- coding: utf-8 -*-
import yaml
from copy import deepcopy
from pathlib import Path

from easydict import EasyDict


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingleConfig(metaclass=SingletonMeta):
    def __init__(self, source='config.yaml'):
        self._keys = list()
        self._source = source
        self.reset()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)

    def __getitem__(self, name):
        return getattr(self, name)

    @staticmethod
    def validate_files(user_config='config.yaml', default_config='config-default.yaml'):
        user_dict = _read_config(user_config)
        sample_dict = _read_config(default_config)

        to_print = list()
        str_to_print = str(user_config)
        result1 = _compare_dict_keys(user_dict, sample_dict, str_to_print, to_print, enable_warnings=True)
        str_to_print = str(default_config)
        result2 = _compare_dict_keys(sample_dict, user_dict, str_to_print, to_print, enable_warnings=False)
        result = result1 and result2

        if len(to_print) > 0:
            print(f'Problem(s) with configs:\n{"".join(to_print)}\nCheck and correct your {_do_bold(user_config)} and '
                  f'{_do_bold(default_config)}!')

        if not result:
            exit(0)
        return result

    def get_part(self, subconfig):
        partial_config = {} if self[subconfig] is None else deepcopy(self[subconfig])
        partial_config.update(self['general'])
        return partial_config

    def reset(self):
        for key in self._keys:
            delattr(self, key)
        self._keys = list()

        d = EasyDict(_read_config(source=self._source))
        for k, v in d.items():
            setattr(self, k, v)
            self._keys.append(k)


def _read_config(source):
    if isinstance(source, str):
        with open(source, 'r') as stream:
            config = yaml.safe_load(stream)
        if config is None:
            print(f'{source} is empty. Fill it, please.')
            exit()
    else:
        raise TypeError('Unexpected source to load config')

    working_dir = Path(config['general']['working_dir']).absolute()
    resources_dir = Path(config['general']['resources_dir']).absolute()
    config['general']['working_dir'] = str(working_dir)
    _set_absolute_paths(config, working_dir, resources_dir)
    return config


def _set_absolute_paths(d, working_dir, resources_dir):
    for key, value in d.items():
        if isinstance(d[key], dict):
            if key.strip() == 'resources':
                for sub_key, sub_value in value.items():
                    value[sub_key] = str(resources_dir.joinpath(sub_value))
            else:
                _set_absolute_paths(d[key], working_dir, resources_dir)
        else:
            if value is not None:
                if 'path' in key:
                    d[key] = str(working_dir.joinpath(value))
                elif 'location' in key:
                    d[key] = str(resources_dir.joinpath(value))


def _compare_dict_keys(subconfig1, subconfig2, str_to_print, to_print, enable_warnings=True):
    result = True
    if type(subconfig1) != type(subconfig2):
        to_print.append(f'{str_to_print} have different types: {type(subconfig1)} and {type(subconfig2)}\n')
        result = False
    elif isinstance(subconfig2, dict):
        for key, value in subconfig2.items():
            if key not in subconfig1:
                to_print.append(f'No key in {str_to_print} {_get_delimiter_key()} {_do_bold(key)}\n')
                result = False
            elif isinstance(value, dict) or isinstance(value, list):
                new_str = f'{str_to_print} {_get_delimiter_key()} {key}'
                cfg1, cfg2 = subconfig1[key], value
                result = _compare_dict_keys(cfg1, cfg2, new_str, to_print, enable_warnings=enable_warnings) and result
    elif isinstance(subconfig2, list):
        if len(subconfig1) == len(subconfig2):
            for idx, (cfg1, cfg2) in enumerate(zip(subconfig1, subconfig2)):
                if isinstance(cfg1, dict) or isinstance(cfg2, list):
                    new_str = f'{str_to_print}[{idx}]'
                    result = _compare_dict_keys(cfg1, cfg2, new_str, to_print, enable_warnings=enable_warnings) \
                             and result
        elif enable_warnings:
            pos = str_to_print.index('>')
            key_description = str_to_print[pos + 2:]
            to_print.append(f'Warning: {key_description} have different length\n')

    return result


def _do_bold(s):
    bold = '\033[1m'
    end_bold = '\033[0m'
    return bold + s + end_bold


def _get_delimiter_key():
    return '->'


def _get_delimiter_key_spaces():
    return ' ' + _get_delimiter_key() + ' '
