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
from datetime import datetime
from typing import Annotated
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import eark_validator.packages as PACKAGES
from eark_validator.specifications.specification import SpecificationVersion

from app.utils import ResultSummary, get_temp_ip_path

from .routers import about, validation

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(about.router)
app.include_router(validation.router)

templates = Jinja2Templates(directory="templates")

@app.get("/", tags=["validate"], response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return RedirectResponse('/static/favicon.ico')

@app.post("/validate", tags=["eark-validator", "commons-ip", "validate"], response_class=HTMLResponse)
async def eark_validate(request: Request, sha1: Annotated[str, Form()], ip_file: UploadFile):
    if not ip_file:
        raise HTTPException(status_code=400, detail="No file upload.")
    package = get_temp_ip_path(ip_file.file, ip_file.filename)
    context = {
        'python_report': PACKAGES.PackageValidator(package, SpecificationVersion.V2_1_0).validation_report,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'python_summary': ResultSummary(PACKAGES.PackageValidator(package, SpecificationVersion.V2_1_0).validation_report)
    }
    return templates.TemplateResponse(request=request, context=context, name="dual_result.html")
