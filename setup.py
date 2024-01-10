from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='pypsola',
    description='Pitch shifting without duration change',
    version='0.0.4',
    author='Joram Millenaar',
    author_email='joormillenaar@live.nl',
    url='https://github.com/jofoks/PyPSOLA',
    install_requires=['numpy'],
    packages=['pypsola'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['audio', 'duration', 'pitch', 'music', 'stretch', 'vocode', 'vocals'],
    license='MIT'
)
