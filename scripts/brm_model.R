#### Preamble ####
# Purpose: Modelling the survey
# Author: Cesar Y. Villarreal Guzman
# Data: 22 October 2020
# License: MIT

#### Workspace Setup ####
library(tidyverse)
library(plyr)
library(brms)
library(tidybayes)

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

#### Model ####
# Basic MR Model
model <- brm(vote_2020 ~ age + gender + hispanic + race_ethnicity + state,
             data = data, 
             family = bernoulli(),
             file = './scripts/models/basic_bayes_model',
             iter = 4000)

# Model intercept on each state
model.int <- brm(vote_2020 ~ age + gender + hispanic + race_ethnicity + (1|state),
             data = data, 
             family = bernoulli(),
             file = './scripts/models/sate_int_model',
             iter = 4000)

# Load the model
model <- read_rds('./scripts/models/fourth_model.rds')

summary(model)

# Import post stratification data
post.strat <- read.csv('post-strat.csv')

# Convert to binary gender and hispanic
post.strat$gender <- post.strat$gender %>%
  mapvalues(from = c("Female", "Male"),
            to = c(0, 1))

post.strat$hispanic <- post.strat$hispanic %>%
  mapvalues(from = c("Hispanic", "Not Hispanic"),
            to = c(1, 0))


## Setting cell counts for pos-stratification
cell_counts <- post.strat %>% 
  group_by(gender, age, race_ethnicity, hispanic, state) %>% 
  summarise(n = sum(perwt)) %>% 
  



summary(post.strat)
summary(data)
