import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="revo_utils",
    version="1.20190428.1",
	author='Robert Binneman',
    author_email="robert@revo.in.na",
    description='A collection of utilities which we use in all our projects',
	long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RobertBinneman/revo_utils/',
    packages=setuptools.find_packages(),
    install_requires=[
        'cryptography',
        'djangorestframework',
        'django',
        'python-dateutil'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: Other :: Proprietary License",
        "Operating System :: OS Independent",
    ],
)