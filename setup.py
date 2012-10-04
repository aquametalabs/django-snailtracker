from setuptools import setup, find_packages

#version = __import__('django_snailtracker').__version__
version = '0.5.7'


setup(name='django-snailtracker',
      version=version,
      description="Track history on django models",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django model-history-tracking',
      author='Kyle Terry',
      author_email='kyle@kyleterry.com',
      url='',
      license='New BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
