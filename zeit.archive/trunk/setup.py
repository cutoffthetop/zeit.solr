from setuptools import setup, find_packages

setup(
    name='zeit.archive',
    version='0.1dev',
    author='Dominik Hoppe',
    author_email='dominik.hoppe@zeit.de',
    url='http://trac.gocept.com/zeit',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'setuptools',
        ],
)
