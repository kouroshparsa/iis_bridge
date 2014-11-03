"""
iis_bridge
-----
iis_bridge is an iis management tool for windows
````````````
* Source
  https://github.com/kouroshparsa/iis_bridge
"""
from setuptools import Command, setup, find_packages


setup(
    name='iis_bridge',
    version='1.0-dev',
    url='https://github.com/kouroshparsa/iis_bridge',
    license='GNU',
    author='Kourosh Parsa',
    description='an iis management tool for windows',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='windows',
    install_requires=[
    ],
    classifiers=[
        'Development Status :: Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU License',
        'Operating System :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)