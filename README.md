## AHRI Python library

The ahri Python library contains classes, methods and functions for
working with and analyzing the [Africa Health Research Institute
(AHRI)](https://www.ahri.org/research/#research-department) datasets.
These can read in the AHRI .dta datasets, save them to pickle (.pkl)
files, set and manage arguments for data processing, and calculate
trends in HIV incidence. This library is based on the [AHRI R
library](https://github.com/vando026/ahri), but work is focused on
speeding up the HIV incidence rate calculations.

The wiki help pages serve as a short introduction to the ahri library.
These can be found in the links below. The help files are organised as
follows:

-   Getting started, which describes how to install the ahri library,
    which AHRI datasets to request and where to put them. It also shows
    how to set the paths to these datasets.
    <https://github.com/vando026/ahri_py/wiki/1-Getting-started>

-   Reading and writing the datasets, which describes the class and
    functions for performing these operations.
    <https://github.com/vando026/ahri_py/wiki/2-DataProc-class-and-methods>

-   Functions to make the HIV incidence datasets, impute the
    seroconversion dates, perform multiple imputation, and calculate
    the annual HIV incidence rates.
    <https://github.com/vando026/ahri_py/wiki/3-HIV-incidence>.


|                                                                                                                                                                                                                                                                        |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Disclaimer: This is not an official AHRI site. The ahri library is a collaboration between researchers using the AHRI datasets. Decisions made in the code about how to use the data are independent of the views, opinions, and policies of AHRI and its employees. |
