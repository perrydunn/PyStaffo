from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as fh:
    requirements = fh.read().splitlines()

setup(
    name='PyStaffo',
    version='0.1.4',
    author='Peregrine Dunn',
    author_email='perrydunn@hotmail.co.uk',
    description='A Staffomatic API Python wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='http://github.com/perrydunn/PyStaffo',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Scheduling'
    ],
    packages=find_packages(),
    install_requires=requirements,
)
