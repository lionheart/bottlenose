from setuptools import setup, find_packages
import sys, os

version = '0.6.4'

install_requires = []
if sys.hexversion <= 0x20600f0: # Check for Python version bundled with json module
    install_requires.append("simplejson>=1.7.1")

setup(name='bottlenose',
      version=version,
      description="A Python hook into the Amazon.com Product Advertising API",
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: Apache Software License",
          ],
      keywords='amazon, product advertising, api',
      author='Dan Loewenherz',
      author_email='dan@dlo.me',
      url='http://github.com/lionheart/bottlenose',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
)
