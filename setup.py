from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in dhananjaya/__init__.py
from dhananjaya import __version__ as version

setup(
	name="dhananjaya",
	version=version,
	description="Donor Management App",
	author="Narahari Dasa",
	author_email="nrhdasa@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)