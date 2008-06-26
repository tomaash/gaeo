#!/usr/bin/env python
from __future__ import with_statement

import os
import sys

from shutil import copytree

def usage(app_name):
    return 'Usage: %s <project name>' % (app_name)

def create_file(file_name, content):
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
    os.makedirs(os.path.dirname(index_html_file))
    create_file(index_html_file, [
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"',
        '    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">',
        '    <head>',
        '        <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />',
        '        <title>GAEO</title>',
        '    </head>',
        '',
        '    <body>',
        '      <h1>It works!!</h1>',
        '    </body>',
        '</html>',
        '',
    ])

def main(project_name):
    cur_dir = os.getcwd()

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
    os.mkdir(application_dir, 0755)
    create_file(os.path.join(application_dir, '__init__.py'), [])

    # create <project_name>/application/controller/welcome.py
    controller_dir = os.path.join(application_dir, 'controller')
    os.mkdir(controller_dir, 0755)
    create_file(os.path.join(controller_dir, '__init__.py'), [])
    # create default controller (welcome.py)
    create_controller_py(os.path.join(controller_dir, 'welcome.py'))

    # create default template
    create_default_template(os.path.join(application_dir, 'templates', 'welcome', 'index.html'))

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

    print 'The "%s" project has been created.' % project_name

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print usage(sys.argv[0]);
