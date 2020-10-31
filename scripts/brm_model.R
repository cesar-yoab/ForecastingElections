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
model <- read_rds('./scripts/models/sate_int_model.rds')

summary(model)


#### Preparing Post Stratification ####
# Import post stratification data
post.strat <- read.csv('post-strat.csv')

# Convert to binary gender and hispanic
post.strat$gender <- post.strat$gender %>%
  plyr::mapvalues(from = c("Female", "Male"),
            to = c(0, 1))

post.strat$hispanic <- post.strat$hispanic %>%
  plyr::mapvalues(from = c("Hispanic", "Not Hispanic"),
            to = c(1, 0))

cell_counts <- post.strat %>% 
  dplyr::group_by(age, gender, race_ethnicity, state, hispanic) %>% 
  dplyr::summarise(n = sum(perwt)) %>% ungroup()

# Proportion stuff
state_prop <- cell_counts %>% 
  dplyr::group_by(state) %>% 
  dplyr::mutate(satate_prop = n/sum(n)) %>% 
  dplyr::ungroup()


#### Generating Predictions ####
results.state <- model %>% 
  add_predicted_draws(newdata = state_prop) %>% 
  rename(vote_predictions = .prediction)

results.state <- results.state %>%
  mutate(vote_predictions_prop = vote_predictions*satate_prop) %>% 
  group_by(state, .draw) %>% 
  summarise(vote_predictions = sum(vote_predictions_prop)) %>% 
  group_by(state) %>% 
  summarise(mean = mean(vote_predictions),
            lower = quantile(vote_predictions, 0.025),
            upper = quantile(vote_predictions, 0.975))


# Save our results
write_csv(results.state, "MRP_Forecast.csv")

# Plot results
results.state %>% ggplot(aes(y = mean, x = forcats::fct_inorder(state), color="MRP Estimates")) +
  geom_point() + 
  geom_errorbar(aes(ymin=lower, ymax=upper), width = 0) + 
  ylab("Proportion Biden support") + 
  xlab("State") + 
  geom_point(data = data %>% 
               group_by(state, vote_2020) %>% 
               summarise(n = n()) %>% 
               group_by(state) %>% 
               mutate(prop = n / sum(n)) %>% 
               filter(vote_2020 == 1),
             aes(state, prop, color = "Raw Data")) + 
  theme_minimal() +
  scale_color_brewer(palette = "Set1") + 
  theme(legend.position = "bottom") +
  theme(legend.title = element_blank())