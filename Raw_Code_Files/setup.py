from cx_Freeze import setup, Executable

# Include all necessary files and packages
includes = ['pygame']
include_files = [('bin', 'bin'),('new_bg.jpg', 'new_bg.jpg'), ('icon.ico', 'icon.ico')]

# Create an executable
exe = Executable(
    script='main.py',
    base='Win32GUI',
    target_name='RoadFighter.exe',
    icon='icon.ico'
)

# Set up the build
setup(
    name='RoadFighter',
    version='1.0',
    description='HCI Group 28 redesign',
    options={
        'build_exe': {
            'includes': includes,
            'include_files': include_files,
        },
    },
    executables=[exe]
)
