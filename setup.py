from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='PyStaffo',
    version='v0.1.0',
    author='Peregrine Dunn',
    author_email='perrydunn@hotmail.co.uk',
    description='A Staffomatic API Python wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='http://github.com/perrydunn/PyStaffo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Scheduling'
    ],
    packages=find_packages(),
    install_requires=['pytz', 'requests>=2.4.2'],
)
