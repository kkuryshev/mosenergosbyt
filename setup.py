from distutils.core import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mosenergosbyt',
    packages=['mosenergosbyt'],
    version='0.1.16',
    license='MIT',
    description='api для работы с порталом мосэнергосбыт',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='@kkuryshev',
    author_email='kkurishev@gmail.com',
    url='https://github.com/kkuryshev/mosenergosbyt',
    keywords=['mosenergosbyt', 'MEANINGFULL', 'KEYWORDS'],
    install_requires=[
        'requests',
        'argparse',
        'python-dateutil'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points = {
        'console_scripts': ['mosenergosbyt=mosenergosbyt.command_line:main'],
    }
)
