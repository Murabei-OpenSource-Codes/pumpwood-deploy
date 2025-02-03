"""setup."""
import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

requirements_path = os.path.join(
    os.path.dirname(__file__), 'requirements.txt')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name='pumpwood-deploy',
    version='1.28.3',
    include_package_data=True,
    license='BSD-3-Clause License',
    description='Package to assist deploy Pumpwood Systems on Kubenets',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Murabei-OpenSource-Codes/pumpwood-deploy',
    author='Murabei Data Science',
    author_email='a.baceti@murabei.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    package_data={'': ['*.yml', '*.sh']},
    install_requires=[
        'jinja2',
        'simplejson>=3.19.3'
    ],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
