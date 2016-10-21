library(tidyverse)

if(!exists("pull_nfl", mode = "function")) source("scripts/pull_nfl.R")
if(!exists("pull_sharks", mode = "function")) source("scripts/pull_sharks.R")
if(!exists("pull_pros", mode = "function")) source("scripts/pull_pros.R")
if(!exists("pull_espn", mode = "function")) source("scripts/pull_espn.R")

df_nfl <- pull_nfl()
df_sharks <- pull_sharks()
df_pros <- pull_pros()
df_espn <- pull_espn()

proj_all <- tibble() %>% 
    bind_rows(df_nfl) %>% 
    full_join(df_sharks) %>% 
    full_join(df_pros) %>% 
    full_join(df_espn)

proj <- proj_all %>% 
    mutate(name = str_trim(name)) %>% 
    mutate(name = str_replace(name, "IR$", "")) %>% 
    group_by(position, name) %>% 
    summarise(
        low = round(min(points),1),
        mid = round(mean(points),1),
        high = round(max(points),1), 
        n = n()) %>% 
    arrange(name) %>% 
    filter(n > 1)

write_csv(proj, "data/proj.csv")
write_csv(proj_all, "data/proj_all.csv")