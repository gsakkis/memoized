import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()
NEWS = open(os.path.join(here, "NEWS.txt")).read()

setup(
    name="memoized",
    version="0.3",
    description="General purpose efficient memoization",
    long_description=README + "\n\n" + NEWS,
    url="https://github.com/gsakkis/memoized",
    license="MIT",
    author="George Sakkis",
    author_email="george.sakkis@gmail.com",
    py_modules=["memoized"],
    package_dir={"": "src"},
    zip_safe=False,
    extras_require={
        "sig": ["decorator"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ]
)
