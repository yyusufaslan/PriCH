from setuptools import setup, find_packages

setup(
    name='PriCH',
    version='0.1.0',
    description='Cross-platform clipboard manager with Tkinter and PostgreSQL',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'psycopg2-binary',
    ],
) 