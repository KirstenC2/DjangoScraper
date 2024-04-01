from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='scraper',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'manage.py = scraper.manage:main',
        ],
    },
)
