library(tidyverse)
library(rvest)
library(stringr)

nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

pull_pros <- function(position = "qb") {
    
    url <- str_c(sep = "",
        "https://www.fantasypros.com/nfl/projections/",
        position, ".php?scoring=STD")
    
    page <- read_html(url) 
    
    name <- page %>% 
        html_nodes("tr") %>% 
        html_nodes(".player-label") %>% 
        html_text() %>% 
        as_tibble() %>% 
        filter(row_number() != 1) %>% 
        rename(name = value)
    
    points_child <- ifelse(
        position == "qb", 11, ifelse(
        position == "rb", 9, ifelse(
        position == "wr", 9, ifelse(
        position == "te", 6, ifelse(
        position == "k", 5, ifelse(
        position == "dst", 11, NA))))))
    
    points <- page %>% 
        html_nodes("tr") %>% 
        html_nodes(str_c(".center:nth-child(", points_child,")")) %>% 
        html_text() %>% 
        as_tibble() %>% 
        rename(points = value)
    
    pros <- bind_cols(name, points) %>% 
        mutate(week = nfl_week) %>% 
        mutate(pos = toupper(position))
}

pros <- pull_pros(position = "k")

# positions to pull
params <- c("qb", "wr", "rb", "te", "k", "dst")

# raw weekly data
pros_raw <- map(params, pull_pros) %>% 
    bind_rows()

