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

import re
from copy import copy
import logging

class Router:
    """ Handles the url routing... """

    class __impl:
        def __init__(self):
            self.__routing_root = {
                'controller': 'welcome',
                'action': 'index',
            }
            self.__pattern_table = {}
            self.__routing_table = []
            # used to store default pattern (but match last)
            self.__routing_table_fallback = [{
                # /:controller/:action
                'pattern': '^/([^/]+)/([^/]+)$',
                'mlist': ['controller', 'action'],
                'm': {'controller': 0, 'action': 1}
            }, {
                # /:controller
                'pattern': '^/([^/]+)$',
                'mlist': ['controller'],
                'm': {'controller': 0, 'action': 'index'}
            }]

        def connect(self, pattern, tbl={}):
            """ Add routing pattern """

            if pattern not in self.__pattern_table:
                p = pattern
                mat = re.findall(':([^/]+)', p)
                for i in range(len(mat)):
                    p = p.replace(':' + mat[i], '([^/]+)')
                    tbl[mat[i]] = i

                if p[0] != '^': p = '^' + p
                if p[-1] != '$': p += '$'

                self.__routing_table.append({
                    'pattern': p,
                    'mlist': mat,
                    'm': copy(tbl),
                })

                self.__pattern_table[pattern] = \
                    len(self.__routing_table) - 1

        def disconnect(self, pattern):
            if pattern in self.__pattern_table:
                idx = self.__pattern_table[pattern]
                del self.__routing_table[idx]
                del self.__pattern_table[pattern]
                
                for k, v in self.__pattern_table.items():
                    if v > idx:
                        self.__pattern_table[k] -= 1

        def root(self, map = {}):
            """ Set the root (/) routing... """
            self.__routing_root['controller'] = \
                map.get('controller', self.__routing_root['controller'])
            self.__routing_root['action'] = \
                map.get('action', self.__routing_root['action'])

        def resolve(self, url):
            """ Resolve the url to the correct mapping """
            
            if url == '/':
                return self.__routing_root
            
            ret = self.__resolveByTable(url, 
                                        self.__routing_table)
            if ret is None: # fallback
                ret = self.__resolveByTable(url, 
                                            self.__routing_table_fallback)

            return ret
        
        def __resolveByTable(self, url, tbl = {}):
            """ Resolve url by the given table """
            for rule in tbl:
                mat = re.findall(rule['pattern'], url)
                mapping = copy(rule['m'])
                if mat:
                    if isinstance(mat[0], tuple):
                        for i in range(len(mat[0])):
                            mapping[rule['mlist'][i]] = mat[0][i]
                    elif isinstance(mat[0], basestring) and rule['mlist']:
                        mapping[rule['mlist'][0]] = mat[0]
                    return mapping
            
            return None

    __instance = None

    def __init__(self):
        if Router.__instance is None:
            Router.__instance = Router.__impl()
        self.__dict__['_Router__instance'] = Router.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
