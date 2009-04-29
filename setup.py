from setuptools import setup, find_packages

setup(
    name = 'zeit.solr',
    version = '0.1dev',
    author = 'Dominik Hoppe',
    author_email = 'dominik.hoppe@zeit.de',
    description = 'Get articles from the repository and prepare them for solr.',
    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    include_package_data = True,
    zip_safe = False,
    namespace = ['zeit'],
    install_requires = [
        'setuptools',
        'zeit.connector',
        'zeit.content.article',
    ],
)
