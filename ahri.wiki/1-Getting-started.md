# AHRI standard production datasets

For the `ahri` library to work, you will need to request five standard
production datasets from the [AHRI Data
Centre](https://www.ahri.org/research/#research-department). For the
2020 release cycle, these standard production datasets are called:

-   RD05-99 ACDIS HIV All.dta

-   SurveillanceEpisodes.dta

-   RD03-99 ACDIS WGH ALL.dta

-   RD04-99 ACDIS MGH ALL.dta

-   RD01-03 ACDIS BoundedStructures.dta

## Folder structure

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
folder.

## Install the library

The `ahri` library is in development, and can be downloaded from GitHub:
<https://github.com/vando026/ahri>. First install the `remotes` package
and then run the following in the R console.

``` r
remotes::install_github('vando026/ahri')
```

Then load the library.

``` r
library(ahri)
```

Note: when you use this method to update to the latest release, you may
have to restart R.

# Setting the file paths

## The setFiles function

The first thing to do is set the file paths to the AHRI datasets. We use
the `setFiles` function for this and assign it to the name `getFiles`.
**The `getFiles` name is required.** In this example, I point `getFiles`
to the 2020 release cycle.

``` r
getFiles <- setFiles(folder="C:/Users/alainv/AHRI_Data/2020")
```

You can inspect the file paths by printing them out:

``` r
getFiles()[1:5]
$hivfile
[1] "C:/Users/alainv/AHRI_Data/2020/RD05-99 ACDIS HIV All.dta"

$epifile
[1] "C:/Users/alainv/AHRI_Data/2020/SurveillanceEpisodes.dta"

$wghfile
[1] "C:/Users/alainv/AHRI_Data/2020/RD03-99 ACDIS WGH ALL.dta"

$mghfile
[1] "C:/Users/alainv/AHRI_Data/2020/RD04-99 ACDIS MGH ALL.dta"

$bsifile
[1] "C:/Users/alainv/AHRI_Data/2020/RD01-03 ACDIS BoundedStructures.dta"
```

If you ommit the folder argument then `setFiles()` will bring up a
graphical dialogue box where you can point and click your way to the
appropriate data folder.

## Changing to different release versions

Since the standard production .dta names should be consistent, the only
parameter that needs to be changed is the folder path. Thus, to call in
the .dta datasets from the 2019 release cycle, I would do:

``` r
getFiles <- setFiles(folder="C:/Users/alainv/AHRI_Data/2019")
```

Each time you start a new `R` session, the `ahri` library will prompt
you to do `getFiles`. It makes sense to have to manually do `getFiles`
each time, since there is no way to guess which data folder you want for
a given project.

`setFiles` also has capabilities for changing the file names, but choose
to do this only if you know what you are doing.

``` r
getFiles <- setFiles(
  folder="C:/Users/alainv/AHRI_Data/2020",
  hivfile="RD06-99 HIV Surveillance.dta",
  epifile="SurveillanceEpisodesExtended.dta")
```

(This document was compiled with `ahri` version 1.2.9 )
