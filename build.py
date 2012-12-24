#!/usr/bin/python
from pythonbuilder.core import use_plugin, init 



use_plugin("python.core")

use_plugin("python.install_dependencies")

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.pylint")
use_plugin("python.flake8")
use_plugin("python.pymetrics")

default_task = "analyze"

@init
def initialize (project):
    project.build_depends_on("mock")
    project.build_depends_on("vkontakte")
    project.build_depends_on("flake8")

    project.set_property('dir_source_main_python', 'src')
    project.set_property('dir_source_main_scripts', 'scripts')
    project.set_property('dir_source_unittest_python', 'test')
    
    project.set_property("coverage_break_build", False)
    project.set_property("pep8_break_build", True)
    
    project.set_property("flake8_verbose_output", True)

