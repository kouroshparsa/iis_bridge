"""
iis_bridge
-----------

iis_bridge is an iis management tool for windows

Link
`````

* Source
  https://github.com/kouroshparsa/

"""
from setuptools import Command, setup, find_packages


setup(
    name='iis_bridge',
    version='0.1',
    url='https://github.com/kouroshparsa/iis_bridge',
    download_url='https://github.com/kouroshparsa/iis_bridge/packages/0.1',
    license='GNU',
    author='Kourosh Parsa',
    author_email="kouroshtheking@gmail.com",
    description='an iis management tool for windows',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='windows',
    install_requires=[
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ]
)