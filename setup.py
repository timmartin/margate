from setuptools import setup

setup(name="margate",
      version='0.0.1',
      description='Faster Django templates',
      author='Tim Martin',
      author_email='tim@asymptotic.co.uk',
      license='MIT',
      packages=['margate'],
      install_requires=['django',
                        'bytecode>=0.5',
                        'funcparserlib>=0.3'],
      zip_safe=False)
