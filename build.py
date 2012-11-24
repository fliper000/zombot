#!/usr/bin/python
from pythonbuilder.core import use_plugin, init 

use_plugin("python.install_dependencies")

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.distutils")

default_task = "publish"

@init
def initialize (project):
    project.build_depends_on("mock")
    project.build_depends_on("pep8")
    project.set_property('dir_source_main_python', 'src')
    project.set_property('dir_source_main_scripts', 'scripts')
    project.set_property('dir_source_unittest_python', 'test')
