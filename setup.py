from setuptools import find_packages, setup

setup(
    name='TracToChatwork',
    version='1.27',
    packages=find_packages(exclude=['*.tests*']),
    entry_points={
        'trac.plugins': [
            'tochatwork.notification = tochatwork.notification',
        ],
    },
)
