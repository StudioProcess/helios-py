from setuptools import setup

def listdir(path):
    '''list files in dir including path of the dir itself'''
    from os import listdir
    return list( map(lambda file: f'{path}/{file}', listdir(path)) )

setup(
    name='helios-py', # required
    version='0.1.0',  # required
    description='Helios Laser DAC',
    url='https://github.com/StudioProcess/helios-py',
    author='Martin Grödl',
    author_email='martin@process.studio',
    py_modules=['Helios', 'helpers', 'matrix'], # modules that aren't part of a package
    data_files=[('lib', listdir('lib'))], # include libs
    platforms=['MacOS, Linux'],
)
