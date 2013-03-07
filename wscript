#!/usr/bin/env python

import os
import Options, Utils
from os import environ

VERSION = "1.0.0"
srcdir = "."
blddir = "build"

def set_options(ctx):
  ctx.tool_options("compiler_cxx")
  ctx.add_option('--debug', action='store_true', help='Run tests with nodeunit_g')
  ctx.add_option('--warn', action='store_true', help='Enable extra -W* compiler flags')

def configure(ctx):
  ctx.check_tool("compiler_cxx")
  ctx.check_tool("node_addon")
  
  if ctx.check(header_name='stdint.h') :
      ctx.env.append_value('CPPFLAGS', ['-DHAVE_STDINT_H=1'])

  ctx.env.append_unique('CXXFLAGS', ['-Wall', '-Wcast-align', '-Wcast-qual',
    '-Wformat-security', '-Wpacked', '-Wpointer-arith',
    '-Wswitch-default', '-Wstrict-aliasing', '-Wimport', '-Winit-self',
    '-Winline', '-Wunsafe-loop-optimizations', '-Wvariadic-macros',
    '-Wwrite-strings', '-Wmissing-field-initializers', '-Wstack-protector',
    '-Wno-long-long'])
  if Options.options.warn:
      # additional flags that do not work well with node-db
      ctx.env.append_unique('CXXFLAGS', ['-Weffc++', '-Wfloat-equal',
        '-Wextra', '-Wswitch-enum', '-Wconversion'])

  nuodb_include = environ.get("NUODB_INCLUDE_DIR", "/opt/local/nuodb/include")
  if nuodb_include:
    ctx.env.append_unique('CXXFLAGS', [ '-I' + nuodb_include ])
  ctx.check(header_name="Connection.h", errmsg="not found; please set NUODB_INCLUDE_DIR", mandatory=True)

  nuodb_lib = environ.get("NUODB_LIB_DIR", "/opt/local/nuodb/lib64")
  if nuodb_lib:
    ctx.env.append_unique('LINKFLAGS', [ '-L' + nuodb_lib ])
  ctx.check_cxx(lib="NuoRemote", errmsg="not found; please set NUODB_LIB_DIR", mandatory=True)
  ctx.env.append_unique('LINKFLAGS', ['-lNuoRemote'])

def build(ctx):
  obj = ctx.new_task_gen("cxx", "shlib", "node_addon")
  obj.target = "nuodb_bindings"
  obj.source = "lib/node-db/binding.cc lib/node-db/connection.cc lib/node-db/events.cc lib/node-db/exception.cc lib/node-db/query.cc lib/node-db/result.cc src/node_db_nuodb_bindings.cc src/node_db_nuodb.cc src/node_db_nuodb_connection.cc src/node_db_nuodb_query.cc src/node_db_nuodb_result.cc"
  obj.includes = "lib/"
  nuodb_lib = environ.get("NUODB_LIB_DIR", "/opt/local/nuodb/lib64")
  obj.rpath = [nuodb_lib] 

def lint(lnt):
  # Bindings C++ source code
  print("Run CPPLint:")
  Utils.exec_command('cpplint --filter=-whitespace/line_length ./lib/node-db/*.h ./lib/node-db/*.cc ./src/*.h ./src/*.cc')
  # Bindings javascript code, and tools
  print("Run Nodelint for sources:")
  Utils.exec_command('nodelint ./package.json ./db-nuodb.js')

def test(ctx):
  test_binary = 'nodeunit'
  if Options.options.debug:
    test_binary = 'nodeunit_g'
  Utils.exec_command(test_binary + ' tests.js')