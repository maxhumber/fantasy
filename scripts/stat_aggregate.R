library(tidyverse)

if(!exists("pull_nfl", mode = "function")) source("scripts/pull_nfl.R")
if(!exists("pull_pros", mode = "function")) source("scripts/pull_pros.R")
if(!exists("pull_sharks", mode = "function")) source("scripts/pull_sharks.R")
if(!exists("pull_espn", mode = "function")) source("scripts/pull_espn.R")

df_nfl <- pull_nfl()
df_pros <- pull_pros()
df_sharks <- pull_sharks()
df_espn <- pull_espn()

df <- tibble() %>% 
    bind_rows(df_nfl) %>% 
    full_join(df_pros) %>% 
    full_join(df_sharks) %>% 
    full_join(df_espn)

df_range <- df %>% 
    mutate(name = str_trim(name)) %>% 
    mutate(name = str_replace(name, "IR$", "")) %>% 
    group_by(position, name) %>% 
    summarise(
        low = round(min(points),1),
        mid = round(mean(points),1),
        high = round(max(points),1), 
        n = n()) %>% 
    arrange(desc(mid)) %>% 
    filter(n > 1)

write_csv(df_range, "data/df_range.csv")
write_csv(df, "data/df.csv")
