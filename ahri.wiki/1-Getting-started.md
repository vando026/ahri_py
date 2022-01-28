AHRI standard production datasets
=================================

For the `ahri` library to work, you will need to request five standard
production datasets from the [AHRI Data
Centre](https://www.ahri.org/research/#research-department). For the
2020 release cycle, these standard production datasets are called:

-   RD05-99 ACDIS HIV All.dta

-   SurveillanceEpisodes.dta

-   RD03-99 ACDIS WGH ALL.dta

-   RD04-99 ACDIS MGH ALL.dta

-   RD01-03 ACDIS BoundedStructures.dta

Folder structure
----------------

AHRI releases updates of the standard production .dta datasets annually,
so it is important to agree on a common folder structure. A suggested
folder structure is to create a root folder with subfolders for the
release year. For example, the path to my root folder is
`C:\Users\alainv\AHRI_Data`, and the folder structure looks like:

    AHRI_Data
    |
    |--- 2018
    |     RD05-99 ACDIS HIV All.dta
    |     SurveillanceEpisodesExtended.dta
    |     RD03-99 ACDIS WGH ALL.dta
    |     RD04-99 ACDIS MGH ALL.dta
    |     RD01-03 ACDIS BoundedStructures.dta      
    |---2019
    |     RD05-99 ACDIS HIV All.dta
    |     SurveillanceEpisodesExtended.dta
    |     RD03-99 ACDIS WGH ALL.dta
    |     RD04-99 ACDIS MGH ALL.dta
    |     RD01-03 ACDIS BoundedStructures.dta      
    |---2020
    |     RD05-99 ACDIS HIV All.dta
    |     SurveillanceEpisodes.dta
    |     RD03-99 ACDIS WGH ALL.dta
    |     RD04-99 ACDIS MGH ALL.dta
    |     RD01-03 ACDIS BoundedStructures.dta      

So folder 2020 holds the datasets from the 2020 release year. Please
make sure you are putting the datasets in the proper release year
folder. (Note that the dataset names can change from year to year.)

Install the library
-------------------

The `ahri` library is in development, and can be cloned from the GitHub
repo:
<a href="https://github.com/vando026/ahri_py" class="uri">https://github.com/vando026/ahri_py</a>.
After cloning, set your working directory to the repo. Alternatively,
make sure you clone the repo to a folder that is on Python’s system
path. For example,

``` python
import sys
print(sys.path[0:3])
```

    ## ['', '/home/alain/miniconda3/envs/py38/bin', '/home/alain/Seafile/Programs/Python/library']

shows the first three system paths on my machine.

Setting the file paths
======================

The first thing to do is set the file paths to the AHRI datasets using
the `SetFiles` class, which is required. The `SetFiles` class has one
argument, which is the root path to the release year of the AHRI data.
On my system it is `'~/Seafile/AHRI_Data/2020'`.

``` python
from ahri.args import *
data2020 = SetFiles(root = '~/Seafile/AHRI_Data/2020')
```

You can inspect the paths that read the `Stata.dta` files by printing
them out:

``` python
data2020.show_read()
```

Changing to different release versions
--------------------------------------

Since the standard production .dta names should be consistent, the only
parameter that needs to be changed is the folder path. Thus, to call in
the .dta datasets from the 2019 release cycle, you can do:

``` python
data2019 = SetFiles(root = '~/Seafile/AHRI_Data/2019')
```

Each time you start a new Python session, the `ahri` library will prompt
you to produce a `SetFiles` instance, since there is no way to guess
which data folder you want for a given project.

`SetFiles` also has capabilities for changing the file names, but choose
to do this only if you know what you are doing.

``` python
data2020 = SetFiles(root = '~/Seafile/AHRI_Data/2020')
data2020.hivfile = "RD003 HIV Surveillance.dta"
```
