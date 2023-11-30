import setuptools
from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    description = f.read()
   
setuptools.setup(
   name='https://github.com/SWE4103-Group2/SWE4103_Group2_Project',
   version='1.0',
   description=description,
   author='SWE4103-Group2',
   packages=['https://github.com/SWE4103-Group2/SWE4103_Group2_Project'],  #same as name
   install_requires=[], #external packages as dependencies
    package_dir={sensor-management-app},
    packages=find_packages("src"),
    python_requires=">=3.6",
)
