import codecs
from setuptools import setup
from setuptools import find_packages

entry_points = {
    'console_scripts': [
        "nti_bake_badge = nti.badges.openbadges.utils.badgebakery:main",
    ],
}

TESTS_REQUIRE = [
    'fudge',
    'pymysql',
    'nti.testing',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.badges',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Badges",
    long_description=(
        _read('README.rst')
        + '\n\n'
        + _read("CHANGES.rst")
    ),
    license='Apache',
    keywords='badges',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/OpenNTI/nti.badges",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'itsdangerous',
        'nti.externalization',
        'nti.property',
        'nti.schema',
        'nti.tahrir-api',
        'nti.wref',
        'Pillow',
        'python-dateutil',
        'requests',
        'simplejson',
        'six',
        'sqlalchemy',
        'zope.component',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.mimetype',
        'zope.security',
        'zope.sqlalchemy',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    entry_points=entry_points,
)
