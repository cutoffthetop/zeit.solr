from setuptools import setup, find_packages

setup(
    name = 'zeit.solr',
    version = '0.12dev',
    author = 'Dominik Hoppe',
    author_email = 'dominik.hoppe@zeit.de',
    description = 'Get articles from the repository and prepare them for solr.',
    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    include_package_data = True,
    zip_safe = False,
    namespace_packages = ['zeit'],
    install_requires = [
        'gocept.async>=0.3.1',
        'grokcore.component',
        'mock',
        'pysolr > 2.0.5',
        'setuptools',
        'simplejson', # for pysolr
        'zeit.cms',
        'zeit.connector',
        'zeit.content.article',
        'zope.index',
    ],
    entry_points = """
        [console_scripts]
        solr-reindex-object = zeit.solr.update:update_main
        solr-reindex-query = zeit.solr.reindex:reindex
        """
)
