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

ROUTES = {
    '/': ('welcome', 'index'),
}

def _resolveUrl(url):
    ret = ROUTES.get(url)

    # use the canonical pattern
    if ret is None:
        ret = re.findall('/([^/]+)/([^/]*).*', url)
        if not ret:
            mat = re.findall('/(.*)', url)
            ret = (mat[0], 'index')
            
    return ret

def dispatch(hnd):
    # resolve the URL
    url = hnd.request.path
    
    route = _resolveUrl(url)
    if route is None:
        logging.error('The request url "%s" is invalid. Redirect it to "/"', url)
        hnd.redirect('/')
    else:
        # create the appropriate controller
        try:
            ctrl = eval('controller.%sController' % route[0].capitalize())(hnd, route)
                       
            # dispatch
            logging.info('URL "%s" is dispatched to: %s -> %s', url, route[0], route[1])
            ctrl.beforeAction()
            getattr(ctrl, route[1], ctrl.index)()
            ctrl.afterAction()
        except AttributeError:  # the controller has not been defined.
            hnd.error(404)                
            hnd.response.out.write('<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1></body</html>')