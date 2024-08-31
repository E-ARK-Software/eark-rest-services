#!/usr/bin/env python
# coding=UTF-8
#
# E-ARK Validation
# Copyright (C) 2019
# All rights reserved.
#
# Licensed to the E-ARK project under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The E-ARK project licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
from functools import lru_cache
import os
import subprocess
from typing import Annotated

from fastapi import Depends

from . import config

from importlib_resources import files
from eark_validator.model import ValidationReport

@lru_cache
def get_settings():
    return config.AppConfig()

settings: Annotated[config.AppConfig, Depends(get_settings)] = get_settings()

MAIN_OPTS = [
    'java',
    '-jar',
    settings.commons_ip_path,
    'validate',
    '-i'
]
REP_OPTS = [
    '-r',
    'eark-validator'
]

def validate_ip(info_pack):
    """Returns a tuple comprising the process exit code, the validation report
    and the captured stderr."""
    ret_code, result, stderr = java_runner(info_pack)
    validation_report = None
    if ret_code == 0:
        file_name = result.decode('utf-8')[result.decode('utf-8').find("'")+1:-1]
        with open(file_name, 'r', encoding='utf-8') as _f:
            contents = _f.read()
        os.remove(file_name)
        validation_report = ValidationReport.model_validate_json(contents)
    else:
        print(f"Validation failed with exit code {ret_code}.")
        print(f"Validation failed with output {result}.")
        print(f"Validation failed with error {stderr}.")
    return ret_code, validation_report, stderr

def java_runner(ip_root):
    command = MAIN_OPTS.copy()
    command.append(ip_root)
    command+=REP_OPTS
    proc_results = subprocess.run(command, capture_output=True)
    return proc_results.returncode, proc_results.stdout.rstrip(), proc_results.stderr
