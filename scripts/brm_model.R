#### Preamble ####
# Purpose: Modelling the survey
# Author: Cesar Y. Villarreal Guzman
# Data: 22 October 2020
# License: MIT

#### Workspace Setup ####
library(tidyverse)
library(plyr)
library(brms)

#### Survey Data Cleaning ####
data <- read.csv('./data/survey-data.csv')

# Convert to binary gender and hispanic
data$gender <- data$gender %>%
  mapvalues(from = c("Female", "Male"),
            to = c(0, 1))

data$hispanic <- data$hispanic %>%
  mapvalues(from = c("Hispanic", "Not Hispanic"),
            to = c(1, 0))

# find . -name '*.csv.gz' -print 0 | xargs -0 -n1 gzip -d

# Second model had smooth training
# Third model had 70 divergent transitions
# Fourth model ...

# Model 2 training
model <- brm(vote_2020 ~ age + gender + hispanic + race_ethnicity + state,
             data = data, 
             family = bernoulli(),
             file = './scripts/fourth_model',
             iter = 4000)

# Model 4 training
model <- brm(vote_2020 ~ age + gender + hispanic + race_ethnicity + (1|state),
             data = data, 
             family = bernoulli(),
             file = './scripts/fourth_model',
             iter = 4000)

# Second model
model <- read_rds('./scripts/second_model.rds')

summary(model)
