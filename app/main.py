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
import logging
from datetime import datetime
from typing import Annotated
from fastapi import Depends, FastAPI, Form, Request, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from eark_validator.cli.app import __version__ as version
import eark_validator.packages as PACKAGES
from eark_validator.specifications.specification import SpecificationVersion
from eark_validator.model import ValidationReport

from app.utils import ResultSummary, get_temp_ip_path
import app.java_runner as JR

from .routers import about, validation
from . import config

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(about.router)
app.include_router(validation.router)
LOG = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")


@app.get("/", tags=["validate"], response_class=HTMLResponse)
async def read_home(request: Request, settings: Annotated[config.AppConfig, Depends(about.get_settings)]):
    context = {
        'eark_validator': version,
        'commons_ip': settings.commons_ip_version
    }
    return templates.TemplateResponse(request=request, context=context, name="home.html")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return RedirectResponse('/static/favicon.ico')

@app.post("/validate", tags=["eark-validator", "commons-ip", "validate"], response_class=HTMLResponse)
async def eark_validate(request: Request, sha1: Annotated[str, Form()], ip_file: UploadFile,  settings: Annotated[config.AppConfig, Depends(about.get_settings)]):
    if not ip_file:
        raise HTTPException(status_code=400, detail="No file upload.")
    package = get_temp_ip_path(ip_file.file, ip_file.filename)
    python_report: ValidationReport = PACKAGES.PackageValidator(package, SpecificationVersion.V2_1_0).validation_report
    java_report = java_validate(package)
    context = {
        'python_report': PACKAGES.PackageValidator(package, SpecificationVersion.V2_1_0).validation_report,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'python_summary': ResultSummary(python_report),
        'java_report': java_report,
        'java_summary': ResultSummary(java_report),
        'compliance': _compliance(python_report, java_report),
        'eark_validator': version,
        'commons_ip': settings.commons_ip_version
    }
    return templates.TemplateResponse(request=request, context=context, name="result.html")

def _compliance(python_report: ValidationReport, java_report: ValidationReport) -> str:
    if python_report.is_valid != java_report.is_valid:
        return 'CONFLICTED'
    elif python_report.is_valid:
        return 'VALID'
    return 'INVALID'

def java_validate(package=None) -> ValidationReport:  # noqa: E501
    """Synchronous package valdition.

    Upload a package binary for validation and return validation result immediately. # noqa: E501

    :param sha1:
    :type sha1: str
    :param ip_file:
    :type ip_file: strstr

    :rtype: ValidationReport
    """
    ret_code, java_report, stderr = JR.validate_ip(package)
    if ret_code != 0:
        LOG.error("Java Runner failed, ret_code: %d, stderr: %s", ret_code, stderr)
    return java_report
