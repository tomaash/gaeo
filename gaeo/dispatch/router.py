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
            self.__routing_table = []
            
            self.connect('/:controller', {'action': 'index'})
            self.connect('/:controller/:action')
            
            
        def connect(self, pattern, tbl = {}):
            """ Add routing pattern """
            p = pattern
            mat = re.findall(':([^/]+)', p)
            for i in range(len(mat)):
                p = p.replace(mat[i], '([^/]+)')
                tbl[mat[i]] = i
            p = p.replace(':', '')

            if p[0] != '^': p = '^' + p
            if p[-1] != '$': p += '$'

            self.__routing_table = [{
                'pattern': p,
                'mlist': mat, 
                'm': copy(tbl),
            }] + self.__routing_table
        
        def root(self, map = {}):
            """ Set the root (/) routing... """
            self.__routing_root['controller'] = map.get('controller', self.__routing_root['controller'])
            self.__routing_root['action'] = map.get('action', self.__routing_root['action'])
        
        def resolve(self, url):
            """ Resolve the url to the correct mapping """
            if url == '/':
                return self.__routing_root

            
            for rule in self.__routing_table:
                mat = re.findall(rule['pattern'], url)
                if mat:
                    logging.error(rule)
                    if type(mat[0]).__name__ == 'tuple':
                        for i in range(len(mat[0])):
                            rule['m'][rule['mlist'][i]] = mat[0][i]
                    elif type(mat[0]).__name__ == 'str' and len(rule['mlist']) > 0:
                        rule['m'][rule['mlist'][0]] = mat[0]
                        
                    return rule['m']
                
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
