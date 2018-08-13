from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='PyStaffo',
    version='v0.0-dev.1',
    author='Peregrine Dunn',
    author_email='perrydunn@hotmail.co.uk',
    description='A Staffomatic API Python wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='http://github.com/perrydunn/PyStaffo',
    packages=find_packages(),
    install_requires=['pytz', 'requests>=2.4.2'],
)
