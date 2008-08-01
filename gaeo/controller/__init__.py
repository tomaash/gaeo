# -*- coding: utf-8 -*-
#
# Copyright 2008 GAEO Team.
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

class BaseController(object):
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

        self._controller = params['controller']
        self._action = params['action']
        self.has_rendered = False
        self.__config = gaeo.Config()

        self.__tpldir = os.path.join(
            self.__config.template_dir,
            self._controller
        )
        self._template_values = {}

        # detect the mobile platform
        self._is_mobile = self.__detect_mobile()
        self._is_iphone = self.__detect_iphone()

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

    def before_action(self):
        pass

    def after_action(self):
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
        self.has_rendered = True

    def redirect(self, url, perm = True):
        self.has_rendered = True # dirty hack, make gaeo don't find the template
        self.hnd.redirect(url, perm)

    def __detect_mobile(self):
        h = self.request.headers

        # wap.wml
        ha = h.get('Accept')
        if ha and (ha.find('text/vnd.wap.wml') > -1 or ha.find('application/vnd.wap.xhtml+xml') > -1):
            return True
        
        wap_profile = h.get('X-Wap-Profile')
        profile = h.get("Profile")
        opera_mini = h.get('X-OperaMini-Features')
        ua_pixels = h.get('UA-pixels')
        
        if wap_profile or profile or opera_mini or ua_pixels:
            return True
        
        # FIXME: add common user agents
        common_uas = ['sony', 'noki', 'java', 'midp', 'benq', 'wap-', 'wapi']
        
        ua = h.get('User-Agent')
        if ua and ua[0:4].lower() in common_uas:
            return True
        
        return False
        
    def __detect_iphone(self):
        """ for detecting iPhone/iPod """
        ua = self.request.headers.get('User-Agent')
        if ua:
            ua = ua.lower();
            return ua.find('iphone') > -1 or ua.find('ipod') > -1
        else:
            return False
