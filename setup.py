from distutils.core import setup

setup(name='webpdb',
      version='0.1',
      description='Remote debugger with web interface',
      author='Andy Jones',
      author_email='andyjones.ed@gmail.com',
      url='https://github.com/andyljones/webpdb',
      packages=['webpdb'],
      package_data={'webpdb': ['resources/*']},
      install_requires = ['flask']
     )