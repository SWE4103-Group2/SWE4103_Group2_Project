from setuptools import setup

with open("README", 'r') as f:
    description = f.read()
   
setup(
   name='https://github.com/SWE4103-Group2/SWE4103_Group2_Project',
   version='1.0',
   description=description,
   author='SWE4103-Group2',
   packages=['https://github.com/SWE4103-Group2/SWE4103_Group2_Project'],  #same as name
   install_requires=[], #external packages as dependencies
)
