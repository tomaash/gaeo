#!/usr/bin/env python
from __future__ import with_statement

import os
import sys
from getopt import getopt
from shutil import copytree

def usage(app_name):
    return 'Usage: %s <project name>' % (app_name)

def create_file(file_name, content):
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name), 0755)
    with open(file_name, 'w') as f:
        f.write('\n'.join(content))

def create_app_yaml(app_yaml_file, project_name):
    create_file(app_yaml_file, [
        'application: %s' % (project_name),
        'version: 1',
        'api_version: 1',
        'runtime: python',
        '',
        'handlers:',
        '- url: /css',
        '  static_dir: assets/css',
        '- url: /js',
        '  static_dir: assets/js',
        '- url: /img',
        '  static_dir: assets/img',
        '- url: /favicon.ico',
        '  static_files: favicon.ico',
        '  upload: favicon.ico',
        '- url: .*',
        '  script: main.py',
        '',
    ])

def create_main_py(main_py_file):
    create_file(main_py_file, [
        "import os",
        "import sys",
        "import wsgiref.handlers",
        "",
        "from google.appengine.ext import webapp",
        "",
        "import gaeo",
        "from gaeo.dispatch import router",
        "",
        "def initRoutes():",
        "    r = router.Router()",
        "    ",
        "    #TODO: add routes here",
        "",
        "    r.connect('/:controller/:action/:id')",
        "",
        "def main():",
        "    # add the project's directory to the import path list.",
        "    sys.path.append(os.path.dirname(__file__))",
        "    sys.path.append(os.path.join(os.path.dirname(__file__), 'application'))",
        "",
        "    # get the gaeo's config (singleton)",
        "    config = gaeo.Config()",
        "    # setup the templates' location",
        "    config.template_dir = os.path.join(",
        "        os.path.dirname(__file__), 'application', 'templates')",
        "",
        "    initRoutes()",
        "",
        "    app = webapp.WSGIApplication([",
        "                (r'.*', gaeo.MainHandler),",
        "            ], debug=True)",
        "    wsgiref.handlers.CGIHandler().run(app)",
        "",
        "if __name__ == '__main__':",
        "    main()",
        "",
    ])


def create_controller_py(controller_py):
    create_file(controller_py, [
        'from gaeo.controller import BaseController',
        '',
        'class WelcomeController(BaseController):',
        '    def index(self):',
        '        pass',
        '',
    ])

def create_default_template(index_html_file):
    create_file(index_html_file, [
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"',
        '    "http://www.w3.org/TR/html4/strict.dtd">',
        '<html>',
        '    <head>',
        '        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">',
        '        <title>GAEO Default Template</title>',
        '    </head>',
        '    <body>',
        '      <h1>It works!!</h1>',
        '    </body>',
        '</html>',
        '',
    ])

def create_eclipse_project(project_home, project_name):
    proj = os.path.join(project_home, '.project')
    pydevproj = os.path.join(project_home, '.pydevproject')
    
    create_file(proj, [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<projectDescription>',
        '    <name>%s</name>' % project_name,
        '    <comment></comment>',
        '    <projects>',
        '    </projects>',
        '    <buildSpec>',
        '        <buildCommand>',
        '            <name>org.python.pydev.PyDevBuilder</name>',
        '            <arguments>',
        '            </arguments>',
        '        </buildCommand>',
        '    </buildSpec>',
        '    <natures>',
        '        <nature>org.python.pydev.pythonNature</nature>',
        '    </natures>',
        '</projectDescription>'
    ])
    
    create_file(pydevproj, [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<?eclipse-pydev version="1.0"?>',
        '',
        '<pydev_project>',
        '    <pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">python 2.5</pydev_property>',
        '    <pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">',
        '        <path>/%s</path>' % project_name,
        '    </pydev_pathproperty>',
        '</pydev_project>'
    ])

def main(argv):
    ignore_exist_proj = False 
    create_eclipse_proj = False

    cur_dir = os.getcwd()

    optlist, args = getopt(argv, '', ['eclipse'])

    for opt, value in optlist:
        if opt == '--eclipse':
            create_eclipse_proj = True

    project_name = args[0]

    # create project directory
    project_home = os.path.join(cur_dir, project_name)
    if os.path.exists(project_home):
        print '%s exists' % (project_home)
        return
    else:
        os.mkdir(project_home, 0755)

    project_name = os.path.basename(project_name).lower()

    # create <project_name>/application/__init__.py
    application_dir = os.path.join(project_home, 'application')
    create_file(os.path.join(application_dir, '__init__.py'), [])

    # create <project_name>/application/controller/welcome.py
    controller_dir = os.path.join(application_dir, 'controller')
    create_file(os.path.join(controller_dir, '__init__.py'), [])
    # create default controller (welcome.py)
    create_controller_py(os.path.join(controller_dir, 'welcome.py'))

    # create default template
    create_default_template(os.path.join(application_dir, 'templates', 'welcome', 'index.html'))

    # create blank model module
    model_dir = os.path.join(application_dir, 'model')
    create_file(os.path.join(model_dir, '__init__.py'), [])

    # create app.yaml
    create_app_yaml(os.path.join(project_home, 'app.yaml'), project_name)

    # create main.py
    create_main_py(os.path.join(project_home, 'main.py'))

    # create assets directories
    assets_dir = os.path.join(project_home, 'assets')
    os.mkdir(assets_dir, 0755)
    for d in ['css', 'img', 'js']:
        target_dir = os.path.join(assets_dir, d)
        os.mkdir(target_dir, 0755)

    # create an empty favicon.ico
    create_file(os.path.join(project_home, 'favicon.ico'), [])

    # copy GAEO directory
    copytree(os.path.join(os.path.dirname(__file__), '..', 'gaeo'), os.path.join(project_home, 'gaeo'))

    # create the eclipse project file
    if create_eclipse_proj:
        create_eclipse_project(project_home, project_name)

    print 'The "%s" project has been created.' % project_name

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        print usage(sys.argv[0]);
