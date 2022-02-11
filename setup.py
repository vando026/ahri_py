from setuptools import Extension, setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ahri",
    version="0.0.3",
    author="Alain Vandormael",
    author_email="vando026@umn.edu",
    description="Modules for analyzing AHRI datasets",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vando026/ahri_py",
    project_urls={
        "Bug Tracker": "https://github.com/vando026/ahri_py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "ahri"},
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires = ['numpy', 'pandas', 'scipy'],
    ext_modules = [Extension("ahri.cyth", ["ahri/cyth.c"])],
)
