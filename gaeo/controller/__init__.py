# -*- coding: utf-8 -*-
#
# Copyright 2008 Lin-Chieh Shangkuan & Liang-Heng Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""GAEO controller package
"""

import os
import logging

from google.appengine.ext.webapp import template

import gaeo
import errors

class BaseController:
    """The BaseController is the base class of action controllers.
        Action controller handles the requests from clients.
    """
    def __init__(self, hnd, params = {}):
        self.resp = hnd.response
        self.req = hnd.request
        self.params = params
        rp = hnd.request.params.mixed()
        for k in rp:
            self.params[k] = rp[k] 
        
        self.__controller = params['controller']
        self.__action = params['action']
        self.__hasRendered = False
        self.__config = gaeo.Config()
        
        self.__tpldir = os.path.join(
            self.__config.template_dir, 
            self.__controller
        )
        self.__template_values = {}
        
    def beforeAction(self):
        pass
    
    def afterAction(self):
        if not self.__hasRendered:
            self.resp.out.write(template.render(
                os.path.join(self.__tpldir, self.__action + '.html'),
                self.__template_values
            ))
            
    def render(self, opt = {}):
        o = self.resp.out
        h = self.resp.headers
        
        if isinstance(opt, basestring):
            h.set('Content-Type', 'text/plain')
            o.write(opt)
        elif isinstance(opt, dict):
            if opt.get('text'):
                o.write(opt.get('text'))
            elif opt.get('json'):
                h['Content-Type'] = 'application/json; charset=utf-8'
                o.write(opt.get('json'))
            elif opt.get('xml'):
                h['Content-Type'] = 'text/xml; charset=utf-8'
                o.write(opt.get('xml'))
            elif opt.get('template'):
                context = {}
                if isinstance(opt.get('values'), dict):
                    context += opt.get('values')
                o.write(template.render(
                    os.path.join(self.__tpldir, template + '.html'),
                    context
                ))
            else:
                raise errors.ControllerRenderTypeError('Missing rendering type')
        self.__hasRendered = True
