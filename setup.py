from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='byerecaptcha',
    version='1.2.4',
    author='Maehdakvan',
    author_email='visitanimation@google.com',
    description='Google Recaptcha solver with selenium.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DedInc/byerecaptcha',
    project_urls={
        'Bug Tracker': 'https://github.com/DedInc/byerecaptcha/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    install_requires = ['opencv-python==4.6.0.66', 'Pillow', 'numpy', 'requests', 'selenium>=4.7.0'],
    python_requires='>=3.6',
)
