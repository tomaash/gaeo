#!/usr/bin/env python
from __future__ import with_statement

import os
import sys

GAEOGEN_VERSION = 0.1

def usage(prog):
    return """Usage: gaeogen.py <generation type> [args]
GAEOGen command line tool, version %s.

Available generation types:

    * controller  - generates a controller class and actions (w/ templates)
    
        usage: gaeogen.py controller <controller_name> [<action1>, <action2>, ..., <actionN>]
    
        e.g.,
        gaeogen.py controller Say
        gaeogen.py controller Product new create edit delete
       

    * model       - generates a data moel class
        
        usage: gaeogen.py model <model_name>
    
        e.g.,
        gaeogen.py model User
      
      
*NOTE* that you should use this tool under your project's directory root.""" % (GAEOGEN_VERSION)

def create_file(file_name, content):
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name), 0755)
    with open(file_name, 'w') as f:
        f.write('\n'.join(content))

def gen_controller(argv):
    cur_dir = os.getcwd()
    
    controller_name = argv[0].lower()
    
    application_dir = os.path.join(cur_dir, 'application')
    controller_dir = os.path.join(application_dir, 'controller')
    template_dir = os.path.join(application_dir, 'templates', controller_name)
    
    controller_content = [
        'from gaeo.controller import BaseController',
        '',
        'class %sController(BaseController):' % controller_name.capitalize(),
    ]

    print 'Creating application/templates/%s/ ...' % controller_name
    os.mkdir(os.path.join(application_dir, 'templates', controller_name), 0755)
    
    if len(argv) < 2:
        controller_content.append('    pass')
    else:
        for arg in argv[1:]:
            print 'Creating application/templates/%s/%s.html ...' % (controller_name, arg)
            create_file(os.path.join(template_dir, '%s.html' % arg), [
                '<h1>%sController#%s</h1>' % (controller_name.capitalize(), arg)
            ])
            controller_content += [
                '    def %s(self):' % arg,
                '        pass',
                ''
            ]
    print 'Creating %s.py ...' % controller_name
    create_file(os.path.join(controller_dir, '%s.py' % controller_name), controller_content)
    
def gen_model(argv):
    cur_dir = os.getcwd()
    
    model_name = argv[0].lower()
    application_dir = os.path.join(cur_dir, 'application')
    model_dir = os.path.join(application_dir, 'model')
    
    # check if the model directory had been created
    if not os.path.exists(os.path.join(model_dir, '__init__.py')):
        create_file(os.path.join(model_dir, '__init__.py'), [])
    
    model_content = [
        'from gaeo.model import BaseModel',
        '',
        'class %s(BaseModel):' % model_name.capitalize(),
        '    pass'
    ]
    print 'Creating Model %s ...' % model_name
    create_file(os.path.join(model_dir, '%s.py' % model_name), model_content)
    
def main(argv):
    gen_type = argv[1].lower()
    if gen_type == 'controller':
        if argv[2] is None:
            print "Usage: %s controller <controller name>" % argv[0]
            sys.exit(1)
        else:
            gen_controller(argv[2:])
    elif gen_type == 'model':
        if argv[2] is None:
            print 'Usage: %s model <model name>' % argv[0]
            sys.exit(1)
        else:
            gen_model(argv[2:])

if __name__ == '__main__':
    if len(sys.argv) < 3 or '--help' in sys.argv or 'help' in sys.argv:
        print usage(sys.argv[0])
        sys.exit(1)
    else:
        main(sys.argv)