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

import new
import os
import re
import logging

from google.appengine.ext.webapp import template

import gaeo
import errors
import helper

class BaseController:
    """The BaseController is the base class of action controllers.
        Action controller handles the requests from clients.
    """
    def __init__(self, hnd, params = {}):
        self.hnd = hnd
        self.resp = self.response = hnd.response
        self.req = self.request = hnd.request
        self.params = params
        
        rp = hnd.request.params.mixed()
        for k in rp:
            self.params[k] = rp[k] 
        
        self.__controller = params['controller']
        self.__action = params['action']
        self.hasRendered = False
        self.__config = gaeo.Config()
        
        self.__tpldir = os.path.join(
            self.__config.template_dir, 
            self.__controller
        )
        self._template_values = {}
        
        # create the session
        try:
            store = self.__config.session_store
            exec('from gaeo.session.%s import %sSession' % 
                (store, store.capitalize()))

            self.session = eval('%sSession' % store.capitalize())(
                                hnd, '%s_session' % self.__config.app_name)
        except:
            raise errors.ControllerInitError('Initialize Session Error!')
            
        # add helpers
        helpers = dir(helper)
        for h in helpers:
            if not re.match('^__.*__$', h):
                self.__dict__[h] = new.instancemethod(eval('helper.%s' % h), self, BaseController)
        
    def beforeAction(self):
        pass
    
    def afterAction(self):
        pass
            
    def render(self, *text, **opt):
        o = self.resp.out
        h = self.resp.headers

        if text:
            h['Content-Type'] = 'text/plain'
            for t in text:
                o.write(str(t))
        elif opt:
            if opt.get('text'):
                o.write(str(opt.get('text')))
            elif opt.get('json'):
                h['Content-Type'] = 'application/json; charset=utf-8'
                o.write(opt.get('json'))
            elif opt.get('xml'):
                h['Content-Type'] = 'text/xml; charset=utf-8'
                o.write(opt.get('xml'))
            elif opt.get('template'):
                context = {}
                if isinstance(opt.get('values'), dict):
                    context.update(opt.get('values'))
                o.write(template.render(
                    os.path.join(self.__tpldir, 
                                 opt.get('template') + '.html'),
                    context
                ))
            else:
                raise errors.ControllerRenderTypeError('Render type error')
        self.hasRendered = True

    def redirect(self, url, perm = True):
        self.hnd.redirect(url, perm)
        