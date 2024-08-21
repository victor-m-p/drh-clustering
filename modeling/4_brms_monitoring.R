# VMP 2024-08-21
library(pacman)
p_load(brms, tidyverse, HDInterval, stringr)

### first look at monitoring ###
data <- read_csv("modeling/monitoring_conversion.csv")

# exclude texts
data_groups <- data |> filter(poll_group == 1) # n = 368

# for now just do Islam or Christianity
mdl_1 <- brm(
    data = data_groups,
    family = bernoulli(link = logit),
    answer_value ~ year_norm + literacy + christian + islamic + (1 + year_norm | world_region),
    prior = c(
        prior(normal(0, 5), class = "b"),
        prior(normal(0, 5), class = "sd"),
        prior(lkj_corr_cholesky(1), class = "L")
    ),
    iter = 8000,
    warmup = 4000,
    control = list(adapt_delta = .99, max_treedepth = 20),
    seed = 542
)

### population effects ###
# so for a one-sided hypothesis posterior probability does exceed 95%
# but we are plotting two-sided 95% credible intervals here
# so does not exceed 97.5% is what a lack of star means.
hypothesis_list <- c("Intercept > 0", "year_norm > 0", "islamic > 0", "christian > 0", "literacy > 0")

evaluate_hypothesis <- function(brms_mdl, hypothesis_string, alpha = 0.025) {
    hypothesis_result <- hypothesis(brms_mdl, hypothesis_string, alpha = alpha)
    as.data.frame(hypothesis_result$hypothesis)
}

df_population <- map_dfr(hypothesis_list, evaluate_hypothesis, brms_mdl = mdl_1)
df_population <- df_population |>
    mutate(across(c(Estimate, Est.Error, CI.Lower, CI.Upper, Evid.Ratio, Post.Prob), ~ round(., 2))) |>
    select(-Star)
write_csv(df_population, "data/mdl/monitoring_conversion_population.csv")

### group effects ###
# Coef is the sum of the population level effect and corresponding group-level effects
# See here: https://cran.r-project.org/web/packages/brms/brms.pdf
hypothesis_regions <- hypothesis(mdl_1, "year_norm > 0", scope = "coef", group = "world_region", alpha = 0.025)
df_group <- as.data.frame(hypothesis_regions$hypothesis)
df_group <- df_group |>
    arrange(desc(Evid.Ratio)) |>
    mutate(across(c(Estimate, Est.Error, CI.Lower, CI.Upper, Evid.Ratio, Post.Prob), ~ round(., 2))) |>
    select(-Star)

write_csv(df_group, "data/mdl/monitoring_conversion_group.csv")

### need summary as well for Rhat and ESS ###
model_summary <- summary(mdl_1)
fixed_summary <- as.data.frame(model_summary$fixed)
fixed_summary$parameter <- rownames(fixed_summary)
write_csv(fixed_summary, "data/mdl/monitoring_conversion_fixed.csv")

random_summary <- as.data.frame(model_summary$random)
random_summary$parameter <- rownames(random_summary)
write_csv(random_summary, "data/mdl/monitoring_conversion_random.csv")
