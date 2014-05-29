from distutils.core import setup
import py2exe  # @UnusedImport
import sys

sys.argv.append('py2exe')

manifest = \
"<?xml version='1.0' encoding='UTF-8' standalone='yes'?> \
<assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'> \
  <trustInfo xmlns=\"urn:schemas-microsoft-com:asm.v3\"> \
    <security> \
      <requestedPrivileges> \
        <requestedExecutionLevel level='asInvoker' uiAccess='false' /> \
      </requestedPrivileges> \
    </security> \
  </trustInfo> \
  <dependency> \
    <dependentAssembly> \
      <assemblyIdentity \
     type='win32' \
     name='Microsoft.VC90.CRT' \
     version='9.0.21022.8' \
     processorArchitecture='*' \
     publicKeyToken='1fc8b3b9a1e18e3b' /> \
    </dependentAssembly> \
  </dependency> \
  <dependency> \
    <dependentAssembly> \
      <assemblyIdentity \
         type=\"win32\" \
         name=\"Microsoft.Windows.Common-Controls\" \
         version=\"6.0.0.0\" \
         processorArchitecture=\"*\" \
         publicKeyToken=\"6595b64144ccf1df\" \
         language=\"*\" /> \
    </dependentAssembly> \
  </dependency> \
</assembly>"

setup(
      options={
               'py2exe': {
                          'bundle_files': 1,
                          'optimize': 2,
                          'compressed': True
                          }
               },
      windows=[{
                'script': 'freightui.py',
                'other_resources' : [(24, 1, manifest)]
                }],
      zipfile=None,
      )
