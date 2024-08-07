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
from fastapi import APIRouter, UploadFile
from eark_validator.cli.app import __version__ as eark_version
import eark_validator.packages as PACKAGES
from eark_validator.model import ValidationReport
from eark_validator.specifications.specification import SpecificationVersion

router = APIRouter()

@router.post("/eark-validator/validate", tags=["eark-validator", "validate"])
async def eark_validate(ip_file: UploadFile) -> ValidationReport:
    report = PACKAGES.PackageValidator(ip_file.filename, SpecificationVersion.V2_1_0).validation_report
    return report

@router.get("/eark-validator/about", tags=["eark-validator", "about"])
async def read_eark_about() -> dict:
    return {"eark-validator version": eark_version }

@router.post("/commons-ip/validate", tags=["commons-ip", "validate"])
async def commons_validate(file: UploadFile) -> ValidationReport:
    return {"validate": "E-ARK Information Package Validation"}

@router.get("/commons-ip/about", tags=["commons-ip", "about"])
async def read_commons_about() -> dict:
    return {"eark-validator version": eark_version }


