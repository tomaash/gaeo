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
import logging

from application import controller

import router

def dispatch(hnd):
    # resolve the URL
    url = hnd.request.path
    r = router.Router()
    route = r.resolve(url)
    if route is None:
        raise Exception('invalid URL')
    else:
        # create the appropriate controller
        try:
            ctrl = eval('controller.%sController' % 
                        route['controller'].capitalize())(hnd, route)
                       
            # dispatch
            logging.info('URL "%s" is dispatched to: %sController#%s', 
                         url, 
                         route['controller'].capitalize(), 
                         route['action'])
            
            ctrl.beforeAction()
            getattr(ctrl, route['action'])()
            ctrl.afterAction()
            
        except AttributeError:  # the controller has not been defined.
            hnd.error(404)                
            hnd.response.out.write('<h1>404 Not Found</h1>')