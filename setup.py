try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.txt", 'r') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="Lab2",
    version="1.0.0",
    description="Lab2",
    long_description=LONG_DESCRIPTION,
    author="Keytus and TheLostLegend",
    author_email="arhi.13.07.2002@mail.ru",
    url="https://github.com/TheLostLegend/S4_PythonLab2",
    license="MIT",
    packages=['Json', 'Pickle'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ]
)