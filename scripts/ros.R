library(tidyverse)

sharks <- read_csv("data/sharks_ros.csv")
nfl <- read_csv("data/nfl_ros.csv")

ros <- full_join(nfl, sharks, by = c("name", "position"), suffix = c("_nfl", "_sharks"))

roster <- c(
    "Andy Dalton",
    "Tyrod Taylor",
    "Ben Roethlisberger",
    "Jonathan Stewart",
    "Matt Forte",
    "Isaiah Crowell",
    "Allen Robinson",
    "Alshon Jeffery",
    "Tyrell Williams",
    "Zach Ertz",
    "Dion Lewis",
    "Bilal Powell",
    "Sammie Coates",
    "Sterling Shepard",
    "Corey Coleman",
    "Adam Vinatieri",
    "Titans")

ros_middle <- ros %>% 
    mutate(ros_total = (ros_total_nfl + ros_total_sharks) / 2) %>% 
    mutate(ros_mean = (ros_mean_nfl + ros_mean_sharks) / 2) %>% 
    mutate(week_points = (week_points_nfl + week_points_sharks) / 2) %>% 
    select(position, name, ros_total:week_points) %>% 
    mutate(team = ifelse(name %in% roster, "Yes", ""))

