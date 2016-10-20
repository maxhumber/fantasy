library(tidyverse)

if(!exists("pull_nfl", mode = "function")) source("scripts/pull_nfl.R")
if(!exists("pull_pros", mode = "function")) source("scripts/pull_pros.R")
if(!exists("pull_sharks", mode = "function")) source("scripts/pull_sharks.R")

df_nfl <- pull_nfl()
df_pros <- pull_pros()
df_sharks <- pull_sharks()

df <- tibble() %>% 
    bind_rows(df_nfl) %>% 
    full_join(df_pros) %>% 
    full_join(df_sharks)
