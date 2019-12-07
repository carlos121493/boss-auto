from setuptools import setup

setup(
    name = 'boss',
    version = '1.0',
    py_modules = ['engine', 'base', 'boss_list', 'boss_monogo', 'detail', 'job'],
    install_requires = ['Click', 'pymongo', 'pandas', 'uiautomator2', 'adbutils', 'tenacity', 'configparser'],
    entry_points='''
        [console_scripts]
        boss=engine:cli
    ''',
)