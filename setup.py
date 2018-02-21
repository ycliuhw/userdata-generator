import os
import sys
from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

VERSION = "0.1.2"

install_requires = [str(ir.req) for ir in parse_requirements("requirements.txt", session=PipSession())]

if __name__ == "__main__":
    setup(
        name="userdata-cool",
        version=VERSION,
        author="Yang Kelvin Liu",
        author_email="ycliuhw@gmail.com",
        license="Apache License 2.0",
        url="https://github.com/ycliuhw/userdata-generator",
        description="Let you write user data easily",
        package_dir={"userdatacool": "src"},
        packages=["userdatacool"],
        keywords=[
            "troposphere",
            "cloudformation",
            "python3",
            "userdata",
        ],
        install_requires=install_requires,
    )
