from cx_Freeze import setup, Executable
import keyring
import os

build_exe_options = {
"packages": ["keyring.backends", "atexit"]
}

		
setup(
        name = "Svaksvat",
        version = "0.5",
        description = "",
        options = {"build_exe": build_exe_options},
        executables = [Executable(
			script="svaksvatgui.py",
			targetName="SvakSvat.exe",
			base="Win32GUI",
		)])
