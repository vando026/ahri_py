AHRI Python library
-------------------

The `ahri` Python library contains classes, methods and functions for
working with and analyzing the [Africa Health Research Institute
(AHRI)](https://www.ahri.org/research/#research-department) datasets.
These can read in the AHRI .dta datasets, save them to pickle (.pkl)
files, set and manange arguments to standardize and subset the data, and
calculate trends in HIV incidence. This library is based on the [AHRI R
library](https://github.com/vando026/ahri), but work is focused on
speeding up the HIV incidence calculations.

The wiki help pages serve as a short introduction to the `ahri` library.
These can be found in the links below. The help files are organised as
follows:

-   Getting started, which describes how to install the `ahri` library,
    which AHRI datasets to request and where to put them. It also shows
    how to set the paths to these datasets.
    <a href="https://github.com/vando026/ahri_py/wiki/1-Getting-started" class="uri">https://github.com/vando026/ahri_py/wiki/1-Getting-started</a>

-   Reading and writing the datasets, which describes the class and
    functions for performing these operations.
    <a href="https://github.com/vando026/ahri_py/wiki/2-Pickle-class-and-methods" class="uri">https://github.com/vando026/ahri_py/wiki/2-Pickle-class-and-methods</a>

-   Set functions, which describes a range of functions for processing
    the data, subsetting the data, and other data tasks.
    <a href="https://github.com/vando026/ahri_py/wiki/3-Set-classes-and-methods" class="uri">https://github.com/vando026/ahri_py/wiki/3-Set-classes-and-methods</a>

-   Functions to make the HIV incidence datasets, impute the
    seroconversion dates, perform multiple imputation, and calculate
    annual HIV incidence.
    <a href="https://github.com/vando026/ahri/wiki_py/4-HIV-incidence" class="uri">https://github.com/vando026/ahri/wiki_py/4-HIV-incidence</a>

-   If you have questions or wish to contribute to code, post them as an
    issue so that I can answer.
    (<a href="https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue" class="uri">https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue</a>)

|                                                                                                                                                                                                                                                                                       |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Disclaimer: This is not an official AHRI site. The `ahri` library is a collaboration between researchers using the AHRI datasets. Decisions made in the code about how to manage and analyze the data are independent of the views, opinions, and policies of AHRI and its employees. |
