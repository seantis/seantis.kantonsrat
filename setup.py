from setuptools import setup, find_packages
import os

name = 'seantis.kantonsrat'
description = (
    "Specialized type and custom organisations for the Kantonsrat of Zug. "
)
version = '0.7'

tests_require = [
    'plone.app.testing',
    'collective.betterbrowser[pyquery]',
    'seantis.plonetools[tests]',
    'mock',
    'freezegun'
]


def get_long_description():
    readme = open('README.rst').read()
    history = open(os.path.join('docs', 'HISTORY.rst')).read()
    contributors = open(os.path.join('docs', 'CONTRIBUTORS.rst')).read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, contributors, history))


setup(
    name=name, version=version, description=description,
    long_description=get_long_description(),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
    ],
    keywords='plone seantis people persons organizations positions kantonsrat',
    author='Seantis GmbH',
    author_email='info@seantis.ch',
    url='https://github.com/seantis/seantis.kantonsrat',
    license='GPL v2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['seantis'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone>=4.3',
        'plone.api',
        'five.grok',
        'plone.app.dexterity [grok, relations]',
        'seantis.people>=0.17',
        'seantis.plonetools>=0.11',
        'collective.dexteritytextindexer',
        'collective.js.jqueryui',
        'reportlab==2.7',
        'pdfdocument',
        'svglib'
    ],
    extras_require=dict(
        tests=tests_require
    ),
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)
