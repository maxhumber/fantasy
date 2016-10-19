library(tidyverse)
library(rvest)
library(stringr)
library(curl)

week <- 7

url <- "http://www.fantasysharks.com/apps/bert/forecasts/projections.php?League=-1&Position=97&scoring=13&Segment=570"

page <- read_html(curl(url, handle = curl::new_handle("useragent" = "Mozilla/5.0")))

name <- page %>% 
    html_nodes(".playerLink") %>% 
    html_text() %>% 
    as_tibble() %>% 
    rename(name = value)

position <- page %>% 
    html_nodes("#toolData td:nth-child(5)") %>% 
    html_text() %>% 
    as_tibble() %>% 
    rename(position = value)

points <- page %>%
    html_nodes("td:nth-child(14)") %>%
    html_text() %>% 
    as_tibble() %>% 
    rename(points = value)

np <- bind_cols(position, name, points) %>% 
    mutate(week = week)
