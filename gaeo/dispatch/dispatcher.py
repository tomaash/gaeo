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
import sys 
from traceback import *

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
    
    def nice_traceback(traceback):
        import sys,re,os
        tb=""
        for line in traceback.splitlines(1):
            filename = re.findall('File "(.+)",', line)
            linenumber = re.findall(', line\s(\d+),', line)
            modulename = re.findall(', in ([A-Za-z]+)', line)
            
            if filename and linenumber and not re.match("<(.+)>",filename[0]):
                fn=filename[0]
                mn="in %s" % modulename[0] if modulename else ""
                fnshort=os.path.basename(fn)
                ln=linenumber[0]
                logging.critical(unicode(fn))
                html="<a href='txmt://open/?url=file://%s&line=%s'>%s:%s %s</a> %s" % (fn,ln,fnshort,ln,mn,line)
                tb+=html
            else:
                tb+=line
        return tb
    
    def show_error(code, log_msg = ''):
        hnd.error(code)
        import sys,re,os
        if sys.exc_info()[0]:
            exception_name = sys.exc_info()[0].__name__
            exception_details = str(sys.exc_info()[1])
            exception_traceback = ''.join(format_exception(*sys.exc_info()))
            special_info = str(exception_details) != str(log_msg)
            logging.error(exception_name)
            logging.error(exception_details)
            logging.error(log_msg)
            logging.error(exception_traceback)
            tb=nice_traceback(exception_traceback)
            if special_info: logging.error(log_msg)
            hnd.response.out.write('<h1>%s</h1>' % HTTP_ERRORS[str(code)])
            hnd.response.out.write('<h3>%s: %s</h3>' % (exception_name, exception_details))
            if special_info: hnd.response.out.write('<pre> %s </pre>' % log_msg)
            hnd.response.out.write('<h1> Traceback </h1>')
            hnd.response.out.write('<pre> %s </pre>' % tb)
        else:
            hnd.response.out.write('<h1> %s </h1>' % log_msg)

    if route is None:
        raise Exception('invalid URL')
    else:
        # create the appropriate controller
        try:
            exec('from controller import %s' % route['controller']) in globals()
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
            show_error(404, "Controller doesn't exist")
        except AttributeError, e:  # the controller has not been defined.
            show_error(404, "Controller doesn't exist")
        except Exception, e:
            show_error(500, e)
        
        else:
            try:
                action = getattr(ctrl, route['action'], None)
                if action is not None:
                    ctrl.implicit_action()
                    ctrl.before_action()
                    action()
                    ctrl.after_action()

                    if not ctrl.has_rendered:
                        ctrl.render(template=route['action'], values=ctrl.__dict__)
                else: # invalid action
                    logging.error('Invalid action `%s` in `%s`' % (route['action'], route['controller']))
                    show_error(404, "Invalid action")
                    # ctrl.invalid_action()
                    ctrl.has_rendered = True
            except Exception, e:
                # import traceback,sys
                # traceback.print_exc(file=sys.stderr)
                show_error(500, e)
