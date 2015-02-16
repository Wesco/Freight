from distutils.core import setup
import py2exe  # @UnusedImport
import sys

sys.argv.append('py2exe')

setup(
    options=
    {
        'py2exe':
        {
            'includes':
            [
                'numpy.linalg._umath_linalg',
                'numpy.fft.fftpack_lite'
            ],
            'bundle_files': 1,
            'optimize': 2,
            'compressed': True
        }
    },
    windows=[{'script': "freight.py"}],
    zipfile=None,
    requires=['pandas', 'xlrd']
)
