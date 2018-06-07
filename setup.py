from setuptools import setup

setup(name='mq-component-py',
      version='0.1.2.1',
      description='Python component for MoniQue.',
      url='https://github.com/biocad/mq-component-py',
      author='Vladimir Morozov',
      author_email='morozovvp@biocad.ru',
      license='BSD3',
      packages=['mq', 'mq.protocol', 'mq.component'],
      zip_safe=False,
      install_requires=['pyzmq', 'msgpack'])
