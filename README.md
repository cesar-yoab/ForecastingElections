# Forecasting Elections

This repository contains all the code used to generate our
presidential elections forecasts. To accomplish this we used the
two techniques multilevel regression and postratification (MRP)
and stacked regression and poststratification (SRP). We used
the Democracy Fund + UCLA Nationscape Survey data to fit our models
and the ACS census data to poststratify our estimates. At the end of the
README we include instructions for reproducing our results.

## 2020 U.S. Presidential Elections Forecast
Both our models estimate Joe Biden to win the popular vote. The table below shows our estimates.

#### Forecast of Popular Vote Proportions:

| Candidate | **MRP Model** | **SRP Model** | The Economist | Wall Street Journal |
|-----------|---------------|---------------|---------------|---------------------|
| Joe Biden | **52.7%** | **54.4%** | 54.2% | 55% |
| Donald Trump | **47.3%** | **45.6%** | 45.8% | 45% |

#### Forecast of Electoral College Votes:

| Candidate | **MRP Model** | **SRP Model** | The Economist | 
|-----------|---------------|---------------|---------------|
| Joe Biden | **401** | **324** | 350 |
| Donald Trump | **137** | **214** | 188 | 


#### Forecast of State Victories
![MRP State Forecast](./util/MRP_state_forecast.png)
![SRP State Forecast](./util/SRP_State_Forecast.png)


## Reproducing Results
NOTE: All our code was created in Ubuntu 19 and therefore the following instructions are for UNIX (Linux, Mac) 
like systems, please use the equivalent Windows commands if that is your operating system.

### Prerequisites
In order to reproduce our results it is important that you have installed R and Python 3.
A requirements.txt file can be found in this repository listing all libraries used, we recommend you create 
python environment to run all our code. You can do this by running the following commands in a terminal

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The R packages used are
1. brms
2. tidyverse
3. knitr
4. cowplot
5. sf
6. urbnmpr

you can install them by typing the following into an R console

```R
install.packages("PACKAGENAME")
```

### Democracy Fund + UCLA Nationscape Survey
First go to the [voter study group website](https://www.voterstudygroup.org/publication/nationscape-data-set)
at the bottom of the page enter your information to request acces to the
data set. We warn you that this may take days and you may not be granted 
permision if you provide an email that is not afiliated to 
an academic institution. When the download is completed move this
file inside of the cloned repository and run the following commands

```bash
mkdir data
mv NATIONSCAPE_FILENAME ./data
source .venv/bin/activate # Only if you have not activated your python environment
python3 scripts/clean_survey.py --unzip --data='./data/THE_DATA_FILENAME'
```
The script should automatically unzip, select the data and clean it. The output is a file
with the name **survey-data.csv**. Make sure you replace "NATIONSCAPE_FILENAME" with the file
name on your computer.


### ACS Data
Now go to the [IPUMS USA website](https://usa.ipums.org/usa/)
create an account if you don't have one, login and follow the next steps:

1. After you login click on the tab **SELECT DATA**
2. Click **SELECT SAMPLES** uncheck "Default sample from each year" and only check **2018 ACS**
3. Click on **Submit Sample Selection** 
4. Under "SELECT HARMONIZED VARIABLES" go to HOUSEHOLD>GEOGRAPHIC and add **STATEFIP** to the cart
5. Go to PERSON>DEMOGRAPHIC and add **SEX** and **AGE** to the cart
6. Go to PERSON>RACE, ETHNICITY, AND NATIVITY and add **RACE** and **HISPAN** to the cart
7. Click on "View Cart" and clik on **CREATE DATA EXTRACT**
8. Download the file (It will be large file!)

After you download the file move it to the cloned repository. If the file you downloaded has
the termination ".csv.gz" then run the following command first

```bash
find . -name '*.csv.gz' -print 0 | xargs -0 -n1 gzip -d
```

This should create a csv file. Then run the following commands

```bash
mv ACS_FILENAME ./data
source .venv/bin/activate
python3 scripts/clean_ipums.py --data='./data/ACS_FILENAME'
```
The script should automatically clean the data and output a file with the name **post-strat.csv**. Make sure
you replace "ACS_FILENAME" with the name of the file in your computer.

### MRP Model
We recommeng you use Rstudio for this step. Instructions on how to install can be 
found [here](https://rstudio.com/). Import the Rproj contained in this repository using
Rstudio. Open the file "brm_model.R" located on the scripts folder and run the script. We 
warn you that this may take a bit since this fil needs to compile a STAN model and train it. 
The script should output a file with the name "MRP_Forecast.csv". This will be the MRP
predictions.

### SPR Model
**WARNING:** The script that trains this model takes approximately 32 min if 4 concurrent workers
are used. If you don't use 4 it may take even longer.

Activate your python environment if you haven't done so and run the following command

```bash
python3 scripts srp_model.py --train='./data/survey-data.csv" --post="post-strat.csv" --n-workers=4
```

Depending on the specs of your computer you may wish to only use 2 concurrent processes but we live this
to your discretion. This script will output a file with the name "spr_forecast.csv". This will be the
SRP predictions.

### (OPTIONAL) Create Report
If you wish to create the report you need to run one last script. Activate your python
environment and run the following

```bash
python3 scripts/electoral_college.py
```

Re-open the R project on Rstudio and open the "report.Rmd" file. Depending on how
you ran the previous commands you may have to change paths in the code chunks, to your
specific case. After you've done this click "Knit" and this should generate the report.pdf file.
We set this as an optional step since the full report is available as a pdf in this repository by
default.