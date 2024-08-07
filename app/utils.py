#!/usr/bin/env python
# coding=UTF-8
#
# E-ARK Validation
# Copyright (C) 2024
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
import os
from pathlib import Path
import tempfile
from typing import Generator

from eark_validator.model import StructureStatus, ValidationReport  # noqa: E501

TEMP = tempfile.gettempdir()
UPLOADS_TEMP = os.path.join(TEMP, 'ip-uploads')
if not os.path.isdir(UPLOADS_TEMP):
    os.makedirs(UPLOADS_TEMP)
ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz', 'gzip'}

def get_temp_ip_path(spooled_file: tempfile.SpooledTemporaryFile, filename: str) -> Path:
    with open(os.path.join(UPLOADS_TEMP, filename), 'wb') as f:
        for chunk in chunk_file(spooled_file):
            f.write(chunk)
    return Path(os.path.join(UPLOADS_TEMP, filename))
        
def chunk_file(file: tempfile.SpooledTemporaryFile, buff_size=4096) -> Generator:
    while True:
        chunk = file.read(buff_size)
        if not chunk:
            break
        yield chunk

class ResultSummary():
    def __init__(self, report: ValidationReport):
        self.errors, self.warnings, self.infos = _get_message_summary(report)
        self.structure = report.structure.status
        self.schema = report.metadata.schema_results if report.metadata else None
        self.schematron = report.metadata.schematron_results if report.metadata else None

    @property
    def is_valid(self) -> bool:
        return self.structure.upper() == StructureStatus.WELLFORMED.upper() and \
            len(self.schema) == 0 and \
            len(self.schematron) == 0

    @property
    def result(self):
        return 'VALID' if self.is_valid else 'NOTVALID'

    def __repr__(self):
        return '{ResultSummary: { "is_valid"="%s", "result"="%s", "structure"="%s", "schema"="%s", "schematron"="%s"}}' \
                % (self.is_valid, self.result, self.structure, self.schema, self.schematron)

def compare_reports(rep_one, rep_two):
    if not rep_one:
        if not rep_two:
            return 'Error'
        return 'Valid' if rep_two.is_valid else 'Invalid'
    if not rep_two:
        return 'Valid' if rep_one.is_valid else 'Invalid'
    if rep_one.is_valid != rep_two.is_valid:
        return 'Conflicted'
    return 'Valid' if rep_one.is_valid else 'Invalid'

def _get_message_summary(report: ValidationReport):
    all_messages = []
    if report.structure:
        all_messages += report.structure.messages
    if report.metadata and report.metadata.schema_results:
        all_messages += report.metadata.schema_results
    if report.metadata and report.metadata.schematron_results:
        all_messages += report.metadata.schematron_results
    return _count_message_types(all_messages)

def _count_message_types(messages):
    infos = 0
    warns = 0
    errs = 0
    for message in messages:
        if message.severity.casefold() == 'information':
            infos+=1
        elif message.severity.casefold() == 'warning':
            warns+=1
        else:
            errs+=1
    return errs, warns, infos