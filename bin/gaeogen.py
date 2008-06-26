#!/usr/bin/env python
from __future__ import with_statement

import os
import sys

def usage(prog):
    return "Usage: %s <generation type> <arg1> <arg2> ... <argN>"

def create_file(file_name, content):
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
    
def main(argv):
    gen_type = argv[1].lower()
    if gen_type == 'controller':
        if argv[2] is None:
            print "Usage: %s controller <controller name>"
            sys.exit(1)
        else:
            gen_controller(argv[2:])

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print usage(sys.argv[0])
        sys.exit(1)
    else:
        main(sys.argv)