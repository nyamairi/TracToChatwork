from setuptools import find_packages, setup

setup(
    name='TracToChatwork',
    version='1.44',
    packages=find_packages(exclude=['*.tests*']),
    entry_points={
        'trac.plugins': [
            'tochatwork.notification = tochatwork.notification',
        ],
    },
)
