from setuptools import setup, find_packages

setup(
    name="kod_master",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kod-master-server=kod_master.main_server:main',
            'kod-master-client=kod_master.main_client:main',
        ],
    },
    python_requires='>=3.7',
) 