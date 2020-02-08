from setuptools import setup, find_packages

setup(
    name="AceGP",
    version="0.0.2",
    author="Eddie Pantridge",
    description="A Genetic Programming system that accretes programs from a stack of expressions and type reification",
    packages=find_packages(exclude=["tests", "examples", "pytypes"]),
    install_requires=[
        "numpy==1.18.1",
        "pandas==0.25.3",
        "typing-inspect==0.5.0",
        "pyrsistent==0.15.7",
    ]
)
