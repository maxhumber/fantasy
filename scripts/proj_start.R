library(tidyverse)

proj <- read_csv("data/proj.csv")

team <- c(
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

proj %>% 
    filter(name %in% team) %>%
    arrange(desc(mid)) %>% 
    mutate(rank = row_number()) %>% 
    ggplot(aes(x = rank, y = mid, color = position)) + 
    geom_linerange(aes(ymin = low, ymax = high)) +
    geom_label(aes(label = name), size = 3) + 
    theme_minimal()