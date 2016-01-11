import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
	'console_scripts': [
		"nti_bake_badge = nti.badges.openbadges.utils.badgebakery:main",
	]
}

TESTS_REQUIRE = [
	'nose',
	'nose-timer',
	'nose-pudb',
	'nose-progressive',
	'nose2[coverage_plugin]',
	'pyhamcrest',
	'nti.nose_traceback_info',
	'nti.testing'
]

setup(
	name='nti.badges',
	version=VERSION,
	author='Jason Madden',
	author_email='jason@nextthought.com',
	description="NTI Badges",
	long_description=codecs.open('README.rst', encoding='utf-8').read(),
	license='Proprietary',
	keywords='pyramid preference',
	classifiers=[
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: Implementation :: CPython'
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti'],
	tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
		'itsdangerous',
		'Pillow',
		'python-dateutil',
		'simplejson',
		'six',
		'sqlalchemy',
		'tahrir-api',
		'transaction',
		'zope.component',
		'zope.interface',
		'zope.lifecycleevent',
		'zope.mimetype',
		'zope.security',
		'zope.sqlalchemy',
		'nti.common',
		'nti.coremetadata',
		'nti.externalization',
		'nti.mimetype',
		'nti.schema',
		'nti.wref'
	],
	extras_require={
		'test': TESTS_REQUIRE,
	},
	entry_points=entry_points
)
