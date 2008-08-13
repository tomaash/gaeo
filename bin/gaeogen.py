#!/usr/bin/env python
from __future__ import with_statement

import os
import sys
import string

GAEOGEN_VERSION = 0.1

def usage():
    return """Usage: gaeogen.py <generation type> [args]
GAEOGen command line tool, version %s.

Available generation types:

    * controller  - generates a controller class and actions (w/ templates)

        usage: gaeogen.py controller <controller_name> [<action1>, <action2>, ..., <actionN>]

        e.g.,
        gaeogen.py controller Say
        gaeogen.py controller Product new create edit delete


    * model       - generates a data model class

        usage: gaeogen.py model <model_name> [<property_name>:<property_type>, ...]

        e.g.,
        gaeogen.py model User

    * scaffold    -

        usage: gaeogen.py scaffold <controller_name> [action, ...] [<property_name>:<property_type>, ...]

*NOTE* that you should use this tool under your project's directory root.""" % (GAEOGEN_VERSION)

def create_file(file_name, content):
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name), 0755)
    with open(file_name, 'w') as f:
        f.write('\n'.join(content))

class GenBase(object):
    def __init__(self, name):
        super(GenBase, self).__init__()
        self.name = name
        self.content = []

    def generate_content(self):
        raise NotImplementedError

    def save(self, file_name):
        self.generate_content()
        create_file(file_name, self.content)

class GenController(GenBase):
    def __init__(self, name):
        super(GenController, self).__init__(name)
        self.actions = {}

    def add_action(self, name, content=['pass']):
        self.actions[name] = content

    def generate_content(self):
        self.content = [
            'from gaeo.controller import BaseController',
            '',
            'import model',
            '',
            'class %sController(BaseController):' % self.name.capitalize(),
        ]

        if not self.actions:
            self.content.append('    pass')

        for act in sorted(self.actions.keys()):
            self.content.append('%sdef %s(self):' % (' ' * 4, act))
            self.content += map(lambda f: ' ' * 8 + f, self.actions[act])
            self.content.append('')

class GenModel(GenBase):
    def __init__(self, name):
        super(GenModel, self).__init__(name)
        self.props = {}

    def add_property(self, arg):
        name, sep, prop = arg.partition(':')
        if name and prop:
            self.props[name] = prop

    def generate_content(self):
        self.content = [
            'from google.appengine.ext import db',
            'from gaeo.model import BaseModel',
            '',
            'class %s(BaseModel):' % self.name.capitalize(),
        ]

        if not self.props:
            self.content.append('    pass')

        for name in sorted(self.props.keys()):
            self.content.append(' ' * 4 + '%s = %s' % (name, self.props[name]))
        self.content.append('')

class GenScaffold(object):
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties

    def create_action(self, action):
        ''' Create action content for controllers '''
        # TODO: add correct content.
        if action == 'new':
            return ['pass']
        elif action == 'create':
            return ['pass']
        else: # default
            return ['pass']

    def create_page(self, action):
        ''' Create HTML page for template '''
        # TODO: add correct content.
        return [
            '<h1>%sController#%s</h1>' % (self.name.capitalize(), action)
        ]

def gen_controller(argv, template_helper=None):
    cur_dir = os.getcwd()

    controller_name = argv[0].lower()
    ctrl = GenController(controller_name)

    application_dir = os.path.join(cur_dir, 'application')
    controller_dir = os.path.join(application_dir, 'controller')
    template_dir = os.path.join(application_dir, 'templates', controller_name)

    if not os.path.exists(template_dir):
        print 'Creating %s ...' % (template_dir)
        os.makedirs(template_dir, 0755)

    for arg in argv[1:]:
        print 'Creating %s/%s.html ...' % (template_dir, arg)

        if template_helper:
            ctrl.add_action(arg, template_helper.create_action(arg))
            create_file(os.path.join(template_dir, '%s.html' % arg),
                template_helper.create_page(arg))
        else:
            ctrl.add_action(arg)
            create_file(os.path.join(template_dir, '%s.html' % arg), [
                '<h1>%sController#%s</h1>' % (controller_name.capitalize(), arg)
            ])
        
    print 'Creating %s/%s.py ...' % (controller_dir, controller_name)
    ctrl.save(os.path.join(controller_dir, '%s.py' % controller_name))
    return ctrl

def gen_model(argv):
    cur_dir = os.getcwd()

    model_name = argv[0].lower()
    application_dir = os.path.join(cur_dir, 'application')
    model_dir = os.path.join(application_dir, 'model')

    # check if the model directory had been created
    if not os.path.exists(os.path.join(model_dir, '__init__.py')):
        create_file(os.path.join(model_dir, '__init__.py'), [])

    mdl = GenModel(model_name)
    for arg in argv[1:]:
        mdl.add_property(arg)        

    print 'Creating Model %s ...' % model_name
    mdl.save(os.path.join(model_dir, '%s.py' % model_name))
    return mdl

def gen_scaffold(argv):
    name = argv[0].lower()

    model_argv = [name]
    ctrlr_argv = [name]

    for arg in argv[1:]:
        if ':' in arg:
            model_argv.append(arg)
        else:
            ctrlr_argv.append(arg)

    gen_model(model_argv)
    scaffold = GenScaffold(name, model_argv[1:])
    gen_controller(ctrlr_argv, scaffold)
    return scaffold

def main(argv):
    gen_type = argv[1].lower()
    try:
        func = eval('gen_%s' % (gen_type))
    except NameError:
        print usage()
        return False

    if argv[2] is None:
        print "Usage: %s %s <%s name>" % (argv[0], gen_type, gen_type)
        return False

    try:
        return func(argv[2:])
    except:
        import traceback
        traceback.print_exc()
        return False
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3 or '--help' in sys.argv or 'help' in sys.argv or not main(sys.argv):
        print usage()
        sys.exit(1)

