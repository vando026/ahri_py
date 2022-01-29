# The Pickle class: read and write methods

Here I describe the class and methods for reading in the .dta datasets and saving them to a Python pickle (.pkl) file. As described in Part 1, start by creating an instance from the
`SetFiles` class, which sets the path to the .dta datasets. On my system:


```python
from ahri.args import SetFiles
path2020 = SetFiles(root = '/home/alain/Seafile/AHRI_Data/2020')
```

    Loading AHRI module


The `Pickle` class provides methods to read in the Stata .dta files. The class also
does some basic data processing and harmonizes variable names for future merging. After reading the data, the `hiv_dta` method will also write a .pkl file to a subfolder called `python` on your `root` path. *You need to create this subfolder yourself.* If you dont, you will get an error message prompting you to do so. For example, on my system it is: '/home/alain/Seafile/AHRI_Data/2020/python'.  



Create an instance from the `Pickle` class as follows:


```python
from ahri.read import Pickle
data2020 = Pickle(paths = path2020)
```

## The Pickle.hiv_dta method
The `hiv_dta` method reads in the `RD05-99 ACDIS HIV All.dta` dataset. It also writes it to a .pkl file, and prints this path when done.


```python
hdat = data2020.hiv_dta(drop15less = True, drop_tasp = True)
hdat.head()
```

    File saved to /home/alain/Seafile/AHRI_Data/2020/python/ACDIS_HIV_All.pkl
    





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IIntID</th>
      <th>BSIntID</th>
      <th>VisitDate</th>
      <th>HIVResult</th>
      <th>Female</th>
      <th>Age</th>
      <th>HIVNegative</th>
      <th>HIVPositive</th>
      <th>Year</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>16</td>
      <td>2830.0</td>
      <td>2009-06-02</td>
      <td>Negative</td>
      <td>1</td>
      <td>56</td>
      <td>2009-06-02</td>
      <td>NaT</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>6</th>
      <td>16</td>
      <td>2830.0</td>
      <td>2011-05-23</td>
      <td>Negative</td>
      <td>1</td>
      <td>58</td>
      <td>2011-05-23</td>
      <td>NaT</td>
      <td>2011</td>
    </tr>
    <tr>
      <th>21</th>
      <td>17</td>
      <td>9274.0</td>
      <td>2004-02-09</td>
      <td>Negative</td>
      <td>1</td>
      <td>35</td>
      <td>2004-02-09</td>
      <td>NaT</td>
      <td>2004</td>
    </tr>
    <tr>
      <th>20</th>
      <td>17</td>
      <td>9274.0</td>
      <td>2005-06-02</td>
      <td>Negative</td>
      <td>1</td>
      <td>36</td>
      <td>2005-06-02</td>
      <td>NaT</td>
      <td>2005</td>
    </tr>
    <tr>
      <th>8</th>
      <td>17</td>
      <td>9274.0</td>
      <td>2006-06-01</td>
      <td>Negative</td>
      <td>1</td>
      <td>37</td>
      <td>2006-06-01</td>
      <td>NaT</td>
      <td>2006</td>
    </tr>
  </tbody>
</table>
</div>



The method takes two arguments: `drop_tasp` and `drop15less`. `drop15less` drops
all HIV tests from participants less than 15 years of age, which is the default. The
`drop_tasp` argument keeps or drops observations from the Treatment-as-Prevention
(TasP) trial areas. In 2017, TasP areas to the North of the PIP surveillance area
were added to the datasets. I think it is safe to drop TasP observations if your
analysis includes data prior to 2017. No-one has systematically studied the demographic and health differences between the TasP and PIP surveillance areas. The .pkl file can be accessed with:




```python
path2020.hiv_pkl
```




    '/home/alain/Seafile/AHRI_Data/2020/python/ACDIS_HIV_All.pkl'



Note, that your decision to drop TasP areas will persist until you change it with another `hiv_dta` statement.

## The Pickle.epi_dta method
The `epi_dta` reads the large `SurveillanceEpisodes.dta` dataset. This dataset is large, approx. ~6 million rows. On my system it takes around 34 seconds to read the Surveillance .dta dataset. 


```python
edat = data2020.epi_dta(drop_tasp = True, addvars = None)
edat.iloc[0:5, 0:6]
```

    Reading data, this may take time...
    File saved to /home/alain/Seafile/AHRI_Data/2020/python/SurveillanceEpisodes.pkl
    





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>IIntID</th>
      <th>BSIntID</th>
      <th>Female</th>
      <th>ExpDays</th>
      <th>ObservationStart</th>
      <th>ObservationEnd</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>11</td>
      <td>2830</td>
      <td>0</td>
      <td>9</td>
      <td>2000-01-01</td>
      <td>2000-01-09</td>
    </tr>
    <tr>
      <th>1</th>
      <td>11</td>
      <td>2830</td>
      <td>0</td>
      <td>33</td>
      <td>2000-01-10</td>
      <td>2000-02-11</td>
    </tr>
    <tr>
      <th>2</th>
      <td>11</td>
      <td>2830</td>
      <td>0</td>
      <td>324</td>
      <td>2000-02-12</td>
      <td>2000-12-31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>11</td>
      <td>2830</td>
      <td>0</td>
      <td>9</td>
      <td>2001-01-01</td>
      <td>2001-01-09</td>
    </tr>
    <tr>
      <th>4</th>
      <td>11</td>
      <td>2830</td>
      <td>0</td>
      <td>356</td>
      <td>2001-01-10</td>
      <td>2001-12-31</td>
    </tr>
  </tbody>
</table>
</div>



The `epi_dta` method has a `drop_tasp` argument, which defaults to `True`. The
`SurveillanceEpisodes.dta` dataset is a bit overwhelming, so by default the `epi_dta`
keeps only variables related to migration (and one or two others), for which this
dataset is best suited. You can however include addtional variables using the
`addvars` argument, which must take a list. For example, you are interested
in adding the employment variables, then do:


```python
# code not run
# data2020.epi_dta(addvars=["CurrentEmployment", "EmploymentType"])
```

The `epi_dta` method writes a .pkl dataset to the following path:


```python
path2020.epi_pkl
```




    '/home/alain/Seafile/AHRI_Data/2020/python/SurveillanceEpisodes.pkl'



## The Pickle.pip_dta method
We can read and load the `RD01-03 ACDIS BoundedStructures.dta` dataset using the `pip_dta` method. 


```python
pdat = data2020.pip_dta()
pdat.head()
```

    File saved to /home/alain/Seafile/AHRI_Data/2020/python/ACDIS_PIP.pkl
    





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>BSIntID</th>
      <th>PIPSA</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>11</td>
      <td>Southern PIPSA</td>
    </tr>
    <tr>
      <th>1</th>
      <td>12</td>
      <td>Southern PIPSA</td>
    </tr>
    <tr>
      <th>2</th>
      <td>13</td>
      <td>Southern PIPSA</td>
    </tr>
    <tr>
      <th>3</th>
      <td>14</td>
      <td>Southern PIPSA</td>
    </tr>
    <tr>
      <th>4</th>
      <td>15</td>
      <td>Southern PIPSA</td>
    </tr>
  </tbody>
</table>
</div>



The primary use of this method is to identify which Bounded Structures (BSIntID) are in the
TasP areas so they can be dropped from the HIV and Surveillance datasets. 
