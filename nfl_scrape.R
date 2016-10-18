library(tidyverse)
library(rvest)
library(jsonlite)
library(stringr)

# "http://fantasy.nfl.com/research/projections?week=6&position=7&offset=0"

# QB - 1
# RB - 2
# WR - 3
# TE - 4
# K - 7
# DEF - 8

# season - statType=seasonProjectedStats
# week - weak = X

# offset = &offset=     BY 25 starting at 0

pull_nfl <- function(week = 1, position = 1, offset = 0) {
    
    url <- str_c(sep = "",
        "http://fantasy.nfl.com/research/projections?", 
        "week=", week, 
        "&position=", position, 
        "&offset=", offset)
    
    page <- read_html(url)
    
    name <- page %>% 
        html_nodes("tbody") %>% 
        html_nodes("tr") %>% 
        html_nodes("td.playerNameAndInfo.first") %>% 
        html_text() %>% 
        as_tibble() %>% 
        rename(Name = value)
    
    points <- page %>% 
        html_nodes("tbody") %>% 
        html_nodes("tr") %>% 
        html_nodes("td.stat.projected.numeric.last") %>% 
        html_text() %>% 
        as_tibble() %>% 
        rename(Points = value)
    
    nfl <- bind_cols(name, points)
}

df <- pull_nfl(week = 7, position = 3)


nfl <- bind_cols(name, points) %>% 
    str_extract(name, "\\sQB\\s")
    separate(
        Name, 
        into = c("Name", "Junk"), 
        sep = "\\sQB\\s|\\sRB\\s|\\sWR\\s|\\sTW\\s|\\sK\\s|\\DEF\\s") %>% 
    select(-Junk)
    


