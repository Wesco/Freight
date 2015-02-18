import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"],
                     "includes": ["pandas", "pytz", "win32timezone"],
                     "excludes": ["tkinter", "PySide", "matplotlib", "scipy"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="freight",
      version="0.1",
      description="Freight processor",
      options={"build_exe": build_exe_options},
      executables=[Executable("freight.py", base=base)],
      requires=['pandas', 'xlrd', 'numpy'])