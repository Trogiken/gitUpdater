from setuptools import setup

setup(
    name='gitUpdater',
    version='0.1.2',
    description='Utilize github to update client programs',
    url='https://github.com/Trogiken/pyexample',
    author='Noah Blaszak',
    author_email='noah.blaszak@gmail.com',
    license='GPL-3.0',
    packages=['updater'],
    install_requires=['requests~=2.25.1', 'packaging~=21.3'],
    python_requires=">=3.6",

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: GPL License',
        'Programming Language :: Python :: 3.6+',
    ],
)
