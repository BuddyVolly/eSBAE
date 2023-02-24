import os
from setuptools import setup, find_packages


def parse_requirements(file):
    return sorted(set(
        line.partition('#')[0].strip()
        for line in open(os.path.join(os.path.dirname(__file__), file))
    )
                  -set('')
                  )

setup(
    name='eSBAE',
    packages=find_packages(),
    include_package_data=True,
    version='0.1',
    description='High-level functionality for the creation of high integrity MRV data',
    install_requires=parse_requirements('requirements.txt'),
    url='https://github.com/sepal-contrib/eSBAE',
    author='Andreas Vollrath, Daniel Guerrero Machado, Pierrick Rambaud, Remi D\'Annunzio',
    author_email='andreas.vollrath[at]fao.org',
    license='MIT License',
    keywords=['MRV', 'SBAE', 'Activity Data',
              'REDD+', 'Remote Sensing', 'Time-series', 
              'High Integrity'],
    zip_safe=False #,
    #setup_requires=['pytest-runner'],
    #tests_require=['pytest']
)
