library(tidyverse)

ros <- read_csv("data/ros.csv")

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
    "Jacquizz Rodgers",
    "Kenny Britt",
    "Sterling Shepard",
    "Corey Coleman",
    "Adam Vinatieri",
    "Buffalo Bills")

ros_middle <- ros %>% 
    mutate(ros_total = (ros_total_nfl + ros_total_sharks) / 2) %>% 
    mutate(ros_mean = (ros_mean_nfl + ros_mean_sharks) / 2) %>% 
    mutate(week_points = (week_points_nfl + week_points_sharks) / 2) %>% 
    select(position, name, ros_total:week_points) %>% 
    mutate(team = ifelse(name %in% roster, "Yes", "")) %>% 
    mutate(target = ifelse(name %in% waivers, "Yes", ""))