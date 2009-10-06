from distutils.core import setup
from distutils.command.build import build
from distutils.command.install import install
from distutils.command.install_lib import install_lib
from distutils.cmd import Command
import distutils.sysconfig
import distutils.ccompiler
import os.path
import sys

DESCRIPTION="""\
Arbitrary precision correctly-rounded floating point arithmetic, via MPFR.\
"""

LONG_DESCRIPTION="""\
The bigfloat module provides a Python wrapper for the MPFR library.
The MPFR library is a well-known, well-tested C library for
arbitrary-precision binary floating point reliable arithmetic; it's
already used by a wide variety of projects, including GCC and SAGE.
It gives precise control over rounding modes and precisions, and
guaranteed reproducible and portable results.  You'll need to have the
MPFR and GMP libraries already installed on your system to use this
module.

Features:

 - correct rounding on all operations;  precisely defined semantics
   compatible with the IEEE 754-2008 standard.

 - the main 'BigFloat' type interacts well with Python integers and
   floats.

 - full support for emulating IEEE 754 arithmetic in any of the IEEE binary
   interchange formats described in IEEE 754-2008.  Infinities, NaNs,
   signed zeros, and subnormals are all supported.
"""


def find_library_file(dirs, libname):
    """Locate the library file for a particular library."""
    # make use of distutils' knowledge of library file extensions
    cc = distutils.ccompiler.new_compiler()
    lib = cc.find_library_file(dirs, libname)
    if lib is None:
        raise ValueError("Unable to locate %s library" % libname)
    return lib

def find_include_file(dirs, libname):
    """Locate the include file for a particular library."""
    includename = libname + '.h'
    for dir in dirs:
        include = os.path.join(dir, includename)
        if os.path.exists(include):
            return include
    # failed to find include file
    raise ValueError("Unable to locate include file for %s library" % libname)

def create_config(infile, outfile, replacement_dict):
    # make substitutions in config file
    outf = open(outfile, 'w')
    for line in open(infile, 'r'):
        for k, v in replacement_dict.items():
            if k in line:
                line = line.replace(k, repr(v))
        outf.write(line)
    outf.close()

class build_config(Command):
    description = "build config file (copy and make substitutions)"

    user_options = [
        ('build-dir=', 'd', 'directory to build in'),
        ]

    def initialize_options(self):
        self.build_dir = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_lib', 'build_dir'))

    def run(self):
        # determine where to look for library files
        library_dirs = ['/usr/local/lib', '/usr/lib']
        if sys.platform == "darwin":
            # fink directory
            library_dirs.append('/sw/lib')
            # macports directory
            library_dirs.append('/opt/local/lib')

        # directory from prefix
        prefix = distutils.sysconfig.get_config_var('prefix')
        if prefix:
            library_dirs.append(os.path.join(prefix, 'lib'))

        # standard locations
        library_dirs.append('/usr/local/lib')
        library_dirs.append('/usr/lib')

        # find mpfr library file
        mpfr_lib = find_library_file(library_dirs, 'mpfr')

        # write config file
        config_in = 'bigfloat_config.py.in'
        self.mkpath(self.build_dir)
        outfile = os.path.join(self.build_dir, 'bigfloat_config.py')
        create_config(config_in, outfile, {'$(MPFR_LIB_LOC)': mpfr_lib})

class BigFloatBuild(build):
    sub_commands = build.sub_commands
    sub_commands.append(('build_config', lambda self:True))

class BigFloatInstallLib(install_lib):
    def build(self):
        install_lib.build(self)
        if not self.skip_build:
            self.run_command('build_config')

def main():

    setup(
        name='bigfloat',
        version='0.1',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author='Mark Dickinson',
        author_email='dickinsm@gmail.com',
        url='http://www.mpfr.org',
        packages=['bigfloat'],

        # Build info
        cmdclass = {
            'build':BigFloatBuild,
            'build_config':build_config,
            'install_lib':BigFloatInstallLib,
#            'install_config':install_config,
            },
        )

if __name__ == "__main__":
    main()

