# AHRI standard production datasets

For the `ahri` library to work, you will need to request five standard production datasets from the [AHRI Data Centre]( https://www.ahri.org/research/#research-department ). For the 2020 release cycle, these standard production datasets are called: 

- RD05-99 ACDIS HIV All.dta

- SurveillanceEpisodes.dta

- RD03-99 ACDIS WGH ALL.dta

- RD04-99 ACDIS MGH ALL.dta

- RD01-03 ACDIS BoundedStructures.dta


## Folder structure


AHRI releases updates of the standard production .dta datasets annually, so it is important to agree
on a common folder structure.  A suggested folder structure is to create a root folder
with subfolders for the release year.  For example, the path to my root folder is
`C:\Users\alainv\AHRI_Data`, and the folder structure looks like:


```
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
```

So folder 2020 holds the datasets from the 2020 release year. Please make sure you are
putting the datasets in the proper release year folder. (Note that the dataset names
can change from year to year.) 


## Install the library

The `ahri` library is in development, and can be cloned from the GitHub repo:
https://github.com/vando026/ahri_py. After cloning, set your working 
directory to the repo. Alternatively, make sure you clone the repo to a
folder that is on Python's system path. For example, the first few paths are shown on my system: 



```python
import sys
print(sys.path[0:2])
```

    ['/home/alain/Seafile/Programs/Python/library/ahri', '/home/alain/Seafile/Programs/Python/library', '/home/alain/miniconda3/envs/py38/lib/python38.zip']


## Setting the file paths

The first thing to do is set the file paths to the AHRI datasets using the `SetFiles` class, which is required. The `SetFiles` class has one argument, which is the root path to the release year of the AHRI data. On my system it is  `'~/Seafile/AHRI_Data/2020'`.




```python
from ahri.args import SetFiles
path2020 = SetFiles(root = '~/Seafile/AHRI_Data/2020')
```

You can inspect the paths that read the `Stata.dta` files by printing out the
instance attribute.




```python
print(path2020.hivfile)
print(path2020.epifile)
print(path2020.bsifile)
```

    ~/Seafile/AHRI_Data/2020/RD05-99 ACDIS HIV All.dta
    ~/Seafile/AHRI_Data/2020/SurveillanceEpisodes.dta
    ~/Seafile/AHRI_Data/2020/RD01-03 ACDIS BoundedStructures.dta


Or, you can use the `show_read` method to see the file paths. 


```python
path2020.show_read()
```

    RD003 HIV Surveillance.dta
    ~/Seafile/AHRI_Data/2020/SurveillanceEpisodes.dta
    ~/Seafile/AHRI_Data/2020/RD01-03 ACDIS BoundedStructures.dta


## Changing to different release versions

Since the standard production .dta names should be (mostly) consistent, the only parameter that needs to be
changed is the folder path. Thus, to call in the .dta datasets from the 2019 release
cycle on my system, I would do:







```python
path2019 = SetFiles(root = '~/Seafile/AHRI_Data/2019')
```
