# ESSD-ASRE
ASRE scripts for the ESSD benchmark

This code is provided as supplementary material with:

* ...: The EUPPBench postprocessing benchmark dataset v1.0, ...

Please cite this article if you use (a part of) this code for a publication.

## Details on the method 

ASRE postprocessing tackles systematic and representativeness errors in two independent steps. 

1.. A local bias correction approach is applied to corrected for systematic errors.
For each station and each lead time, the averaged difference between reforecasts and observations in the training dataset is computed and removed from the forecast in the validation dataset. Parctically, the bias is estimated for each station ( $s$ ), each forecast lead time ( $t$ ), and each day of the year ( $d$ ) by computing the difference between forecast ( $f$ ) and observation ( $o$ ) over a training window. The training window is centered around the forecast day $d$. Practically, the bias $b$ is estimated as follows: 

$$b_{s,t,d} = \frac{1}{N_w} \sum_{d_i=d-w/2}^{d+w/2} {f_{s,t,d_i} -o_{s,t,d_i}}, $$

with $w$ the size of the temporal window around day $d$ and $N_w$ the number of forecast/observation pairs within this averaging window. In our experiment, we set $w=60$ days. This bias correction approach is local as it is a function of $s$.

2.. Representativeness errors are accounted for separately using a universal method inspired by the \textit{Perfect Prog} approach. A normal distribution is used to represent the diversity of temperature values that can be observed at a point within an area given the average temperature of that area. Practically, noise is added to each ensemble member by drawing from a distribution $\mathcal{N}(0,\sigma({\Delta})^2)$ where $\sigma$ is a function of the length of area \Delat (or gridbox size) defined as follows: 

$$ \sigma  = \beta_0(\Delta) + \beta_1(\Delta) \sqrt[4]{\mid e_\textrm{m} - e_\textrm{o} \mid }, $$

where $e_\textrm{o}$ and $e_\textrm{m}$ denote the elevation of the observation and the corresponding model orography at the nearest model grid point, respectively.  The coefficients $\beta_0$ and $\beta_1$ depends only on the model grid resolution $\Delta$ as defined by Eq. 4 in [Ben Bouallegue 2020](https://www.ecmwf.int/sites/default/files/elibrary/2020/19544-accounting-represenstativeness-verification-ensemble-forecasts.pdf). In our experiment, we set $\Delta=18$ km.


## Data and usage

The script is build around the ESSD benchmark dataset.
This dataset can be downloaded using [the download script](https://github.com/EUPP-benchmark/ESSD-benchmark-datasets). This will fetch the dataset into NetCDF files on your disk.


