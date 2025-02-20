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
from pathlib import Path
from hashlib import sha1
import shutil
import tempfile
import zipfile
from typing import Generator

from eark_validator.model import StructureStatus, ValidationReport
from eark_validator.model.validation_report import MetadataStatus, Result, Severity  # noqa: E501
from eark_validator.infopacks.package_handler import PackageHandler

TEMP = tempfile.gettempdir()
UPLOADS_TEMP = Path(TEMP) / 'ip-uploads'
if not UPLOADS_TEMP.is_dir():
   UPLOADS_TEMP.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz', 'gzip'}

def get_temp_ip_path(spooled_file: tempfile.SpooledTemporaryFile, filename: str) -> Path:
    temp_path = UPLOADS_TEMP / filename
    digest = sha1()
    with open(temp_path, 'wb') as f:
        for chunk in chunk_file(spooled_file):
            digest.update(chunk)
            f.write(chunk)
    if (PackageHandler.is_archive(temp_path) and not zipfile.is_zipfile(temp_path)):
        package_handler = PackageHandler()
        temp_path = package_handler.unpack_package(temp_path, UPLOADS_TEMP)
        hex_path = UPLOADS_TEMP / digest.hexdigest()
    else:
        hex_path = UPLOADS_TEMP / (digest.hexdigest() + Path(filename).suffix)
    if (not hex_path.exists()):
        temp_path.rename(hex_path)
    return hex_path
        
def chunk_file(file: tempfile.SpooledTemporaryFile, buff_size=4096) -> Generator:
    while True:
        chunk = file.read(buff_size)
        if not chunk:
            break
        yield chunk

class ResultSummary():
    def __init__(self, report: ValidationReport):
        self.errors, self.warnings, self.infos = _get_message_summary(report)
        self.structure_status = report.structure.status
        self.metadata_status = MetadataStatus.VALID if ((report.metadata != None) and report.metadata.schema_results.status == report.metadata.schematron_results.status == MetadataStatus.VALID) else MetadataStatus.INVALID
        self.schema = report.metadata.schema_results.messages if report.metadata and report.metadata.schema_results else None
        self.schematron = report.metadata.schematron_results.messages if report.metadata and report.metadata.schematron_results else None

    @property
    def is_valid(self) -> bool:
        return self.structure_status.upper() == StructureStatus.WELLFORMED.upper() and self.metadata_status == MetadataStatus.VALID

    @property
    def result(self):
        return 'VALID' if self.is_valid else 'NOTVALID'

    def __repr__(self):
        return '{ResultSummary: { "is_valid"="%s", "result"="%s", "structure"="%s", "schema"="%s", "schematron"="%s"}}' \
                % (self.is_valid, self.result, self.structure_status, self.schema, self.schematron)

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
    if report.metadata and report.metadata.schema_results and report.metadata.schema_results.messages:
        all_messages += report.metadata.schema_results.messages
    if report.metadata and report.metadata.schematron_results and report.metadata.schematron_results.messages:
        all_messages += report.metadata.schematron_results.messages
    return _count_message_types(all_messages)

def _count_message_types(messages: list[Result]):
    infos = 0
    warns = 0
    errs = 0
    for message in messages:
        if message.severity == Severity.INFORMATION:
            infos+=1
        elif message.severity == Severity.WARNING:
            warns+=1
        else:
            errs+=1
    return errs, warns, infos