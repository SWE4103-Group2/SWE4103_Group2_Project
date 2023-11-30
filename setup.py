import setuptools
from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    description = f.read()
   
setuptools.setup(
   name='SWE4103_Group2_Project',
   version='1.0',
   description=description,
   author='SWE4103-Group2',
   packages=['src'],  #same as name
   install_requires=[], #external packages as dependencies
    url="https://github.com/SWE4103-Group2/SWE4103_Group2_Project",
)
