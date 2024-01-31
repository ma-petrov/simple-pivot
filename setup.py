from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='simple-pivot',
    version='0.2',
    license='MIT',
    author='Mikhail Petrov',
    author_email='petrov.ma@icloud.com',
    description="",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['pandas'],
    test_requires=[],
    project_urls = {
        'Github': 'https://github.com/ma-petrov/simple-pivot',
    },
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)