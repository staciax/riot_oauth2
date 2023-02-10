import re

from setuptools import setup

# inspired by https://github.com/Rapptz/discord.py/blob/master/setup.py

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('riot_oauth2/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

readme = ''
with open('README.md', encoding='utf-8') as f:
    readme = f.read()

packages = ['riot_oauth2']

setup(
    name='riot_oauth2',
    author='staciax',
    url='https://github.com/staciax/riot_oauth2',
    project_urls={
        'Issue tracker': 'https://github.com/staciax/riot_oauth2/issues',
    },
    version=version,
    packages=packages,
    license='MIT',
    description='A basic wrapper for the Riot Games OAuth2 API.',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    python_requires='>=3.8.0',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
