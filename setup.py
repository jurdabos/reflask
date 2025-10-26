from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name='Reflask',
    packages=find_packages(exclude=['examples']),
    version='0.2.0',
    license='MIT',
    description='Reflask: study project for IU class From Model to Production',
    author='Torda Balázs',
    author_email='balazs.torda@iu-study.org',
    url='https://github.com/jurdabos/reflask',
    install_requires=requirements,
)