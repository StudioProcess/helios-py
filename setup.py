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
    packages=['helios'], # required
    # include_package_data=True, # automatically includes data files (lib dir, in this case) -> doesn't seem to work when installing from git
    package_data={ 'helios': ['lib/*'] }, # inlcude lib files
    platforms=['MacOS, Linux'],
)
