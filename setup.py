#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    import setuptools
    from setuptools import setup, find_packages
except ImportError:
    print('Please install setuptools.')

    def find_scripts(scripts_path):
        base_path = os.path.abspath(scripts_path)
        make_path = lambda path: os.path.join(scripts_path, path)
        is_file = lambda file_name: os.path.isfile(
            os.path.join(base_path, file_name))
        return list(map(make_path, filter(is_file, os.listdir(base_path))))

import os
import sys

libdir = '.'

sys.path.insert(0, libdir)

import info
import version

setup_options = info.INFO
setup_options['version'] = version.VERSION
setup_options.update(
    {
        'install_requires': open('requirements.txt').read().splitlines(),
        'packages': find_packages(libdir),
        'package_dir': {'': libdir},
    }
)

setup(**setup_options)
