"""tensorflow/datasets is a library of datasets ready to use with TensorFlow.

tensorflow/datasets is a library of public datasets ready to use with
TensorFlow. Each dataset definition contains the logic necessary to download and
prepare the dataset, as well as to read it into a model using the
`tf.data.Dataset` API.

Usage outside of TensorFlow is also supported.

See the README on GitHub for further documentation.
"""

import sys

from setuptools import find_packages
from setuptools import setup

DOCLINES = __doc__.split('\n')

REQUIRED_PKGS = [
    'future',
    'protobuf',
    'pytz',
    'requests',
    'six',
    'tqdm',
]

TESTS_REQUIRE = [
    'absl-py',
    'jupyter',
    'pytest',
]

if sys.version_info.major == 3:
  # Packages only for Python 3
  pass
else:
  # Packages only for Python 2
  TESTS_REQUIRE.append('mock')
  REQUIRED_PKGS.append('futures')  # concurrent.futures

if sys.version_info < (3, 4):
  # enum introduced in Python 3.4
  REQUIRED_PKGS.append('enum34')


setup(
    name='tensorflow-datasets',
    version='0.0.1',
    description=DOCLINES[0],
    long_description='\n'.join(DOCLINES[2:]),
    author='Google Inc.',
    author_email='opensource@google.com',
    url='http://github.com/tensorflow/datasets',
    download_url='https://github.com/tensorflow/datasets/tags',
    license='Apache 2.0',
    packages=find_packages(),
    package_data={},
    scripts=[],
    install_requires=REQUIRED_PKGS,
    extras_require={
        'tensorflow': ['tf-nightly>=1.12.0.dev20181008'],
        'tensorflow_gpu': ['tf-nightly-gpu>=1.12.0.dev20181008'],
        'tests': TESTS_REQUIRE,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='tensorflow machine learning datasets',
)
