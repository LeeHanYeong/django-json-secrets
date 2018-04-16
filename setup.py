import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-json-secrets',
    version='0.1.9',
    description='JSON secrets to Django settings module',
    long_description=README,
    # long_description_content_type='text/markdown',
    author='lhy',
    author_email='dev@lhy.kr',
    license='MIT',
    packages=[
        'djs',
    ],
    url='https://github.com/LeeHanYeong/django-json-secrets',
    zip_safe=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
