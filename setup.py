import setuptools


import classarg


with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name=classarg.__name__,
    version=classarg.__version__,
    author=classarg.__author__,
    author_email=classarg.__email__,
    description='A library for easily creating CLI applications.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/IanChen83/ClassArg',
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Utilities',
    ),
)
