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

import router

HTTP_ERRORS = {
    '400': 'Bad Request',
    '402': 'Payment Required',
    '403': 'Forbidden',
    '404': 'Not Found',
    '500': 'Internal Server Error'
}

def dispatch(hnd):
    # resolve the URL
    url = hnd.request.path
    r = router.Router()
    route = r.resolve(url)
    
    def show_error(code, log_msg = ''):
        hnd.error(code)
        logging.error(msg)
        hnd.response.out.write('<h1>%s</h1>' % HTTP_ERRORS[str(code)])
    
    if route is None:
        raise Exception('invalid URL')
    else:
        # create the appropriate controller
        try:
            exec('from controller import %s' % route['controller'])
            ctrl = eval('%s.%sController' % (
                        route['controller'],
                        route['controller'].capitalize()
                    ))(hnd, route)

            # dispatch
            logging.info('URL "%s" is dispatched to: %sController#%s',
                         url,
                         route['controller'].capitalize(),
                         route['action'])
        except ImportError, e:
            show_error(404, e)
        except AttributeError, e:  # the controller has not been defined.
            show_error(404, e)
        else:
            try:
                action = getattr(ctrl, route['action'], None)
                if action is not None:
                    ctrl.before_action()
                    action()
                    ctrl.after_action()

                    if not ctrl.has_rendered:
                        ctrl.render(template=route['action'], values=ctrl.__dict__)
                else: # invalid action
                    logging.error('Invalid action `%s` in `%s`' % (route['action'], route['controller']))
                    ctrl.invalid_action()
                    ctrl.has_rendered = True
            except Exception, e:
                import traceback,sys
                traceback.print_exc(file=sys.stderr)
                show_error(500, e)
