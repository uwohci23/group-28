from cx_Freeze import setup, Executable

# Include all necessary files and packages
includes = []
include_files = [('bin', 'bin'), ('new_bg.jpg', 'new_bg.jpg'), ('icon.icns', 'icon.icns')]

# Create an executable
exe = Executable(
    script='main.py',
    base='MacOSX',
    targetName='RoadFighter.app',
    icon='icon.icns'
)
# Set up the build
setup(
    name='RoadFighter',
    version='1.0',
    description='HCI Group 28',
    options={
        'build_exe': {
            'includes': includes,
            'include_files': include_files,
            'packages': ['pygame'],
            'include_msvcr': True,
        },
        'bdist_mac': {
            'bundle_name': 'MyGame',
            'iconfile': 'icon.icns',
        },
    },
    executables=[exe]
)
