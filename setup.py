from setuptools import find_packages, setup

setup(
    name='TracToChatwork',
    version='1.72',
    packages=find_packages(exclude=['*.tests*']),
    package_data={
        'tochatwork': ['templates/*.html'],
    },
    entry_points={
        'trac.plugins': [
            'tochatwork.notification = tochatwork.notification',
            'tochatwork.admin_panel = tochatwork.admin_panel',
        ],
    },
)
