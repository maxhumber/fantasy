library(tidyverse)
library(stringr)

if(!exists("pull_nfl", mode = "function")) source("scripts/pull_nfl.R")
if(!exists("pull_sharks", mode = "function")) source("scripts/pull_sharks.R")

ros_nfl <- pull_nfl(.season = TRUE)
ros_sharks <- pull_sharks(.season = TRUE)

ros <- bind_rows(ros_nfl, ros_sharks) %>% 
    mutate(name = str_trim(name)) %>% 
    group_by(position, name, week) %>% 
    summarise(
        low = round(min(points),1),
        mid = round(mean(points),1),
        high = round(max(points),1)) %>% 
    arrange(name)

write_csv(ros, "data/ros.csv")