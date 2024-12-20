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
from functools import lru_cache
from typing import Annotated

from eark_validator.cli.app import __version__ as version
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import config

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@lru_cache()
def get_settings():
    return config.AppConfig()

@router.get("/about", tags=["about"], response_class=HTMLResponse)
async def read_home(request: Request, settings: Annotated[config.AppConfig, Depends(get_settings)]):
    context = {
        'config': {
            'eark-validator': version,
            'commons-ip': settings.commons_ip_version
    }       }
    return templates.TemplateResponse(request=request, context=context, name="about.html")
