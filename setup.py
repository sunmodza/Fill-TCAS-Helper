from cx_Freeze import setup, Executable

base = None

executables = [Executable("main.py", base=base)]

packages = []
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "TcasFiller",
    options = options,
    version = "1",
    description = 'good',
    executables = executables
)