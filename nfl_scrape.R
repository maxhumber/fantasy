library(tidyverse)
library(rvest)
library(jsonlite)
library(stringr)

# QB - 1
# RB - 2
# WR - 3
# TE - 4
# K - 7
# DEF - 8

# season - statType=seasonProjectedStats
# week - weak = X

# offset = &offset=     BY 25 starting at 0

url <- read_html("http://fantasy.nfl.com/research/projections?week=6&position=7&offset=0")

name <- url %>% 
    html_nodes("tbody") %>% 
    html_nodes("tr") %>% 
    html_nodes("td.playerNameAndInfo.first") %>% 
    html_text() %>% 
    as_tibble() %>% 
    rename(Name = value)

points <- url %>% 
    html_nodes("tbody") %>% 
    html_nodes("tr") %>% 
    html_nodes("td.stat.projected.numeric.last") %>% 
    html_text() %>% 
    as_tibble() %>% 
    rename(Points = value)

nfl <- bind_cols(name, points) %>% 
    separate(
        Name, 
        into = c("Name", "Junk"), 
        sep = "\\sQB\\s|\\sRB\\s|\\sWR\\s|\\sTW\\s|\\sK\\s|\\DEF\\s") %>% 
    select(-Junk)
    


