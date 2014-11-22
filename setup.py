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
    version='0.8',
    url='https://github.com/kouroshparsa/iis_bridge',
    download_url='https://github.com/kouroshparsa/iis_bridge/packages/0.8',
    license='GNU',
    author='Kourosh Parsa',
    author_email="kouroshtheking@gmail.com",
    description='an iis management tool for windows',
    long_description=__doc__,
    packages=find_packages(),
    install_requires = ['Jinja2>=2.7.3'],
    include_package_data=True,
    package_data = {'iis_bridge': ['templates/*.html']},
    zip_safe=False,
    platforms='windows',
    classifiers=[
        'Environment :: Web Environment',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ]
)