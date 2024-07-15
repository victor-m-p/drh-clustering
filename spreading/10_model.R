library(pacman)
p_load(brms, tidyverse, HDInterval, stringr)

data_conversion <- read_csv("spreading/data/conversion_model.csv")

fit_conversion <- brm(
    data = data_conversion,
    family = bernoulli(link = logit),
    answer_value_to ~ 1 + avg_yes + avg_christian,
    iter = 4000,
    warmup = 2000,
    chains = 4,
    cores = 4,
    control = list(adapt_delta = .99, max_treedepth = 20),
)

summary(fit_conversion) # christian is a better predictor than yes

data_unquestionably <- read_csv("spreading/data/unquestionably_model.csv")

fit_unquestionably <- brm(
    data = data_unquestionably,
    family = bernoulli(link = logit),
    answer_value_to ~ 1 + avg_yes + avg_christian,
    iter = 4000,
    warmup = 2000,
    chains = 4,
    cores = 4,
    control = list(adapt_delta = .99, max_treedepth = 20),
)

summary(fit_unquestionably) # yes stronger than christian (not significant here)

fit_unquestionably_2 <- brm(
    data = data_unquestionably,
    family = bernoulli(link = logit),
    answer_value_to ~ 1 + avg_christian,
    iter = 4000,
    warmup = 2000,
    chains = 4,
    cores = 4,
    control = list(adapt_delta = .99, max_treedepth = 20)
)

summary(fit_unquestionably_2) # is when we do not control (but just proxies for "YES")
