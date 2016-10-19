library(tidyverse)
library(rvest)
library(stringr)
library(curl)

week <- 7

url <- str_c(sep = "",
     "http://www.fantasysharks.com/apps/bert/forecasts/projections.php?", 
        # no league
     "League=-1",
         # QB + RB + WR + TE = 97
         # K - 7
         # DEF - 6
     "Position=", 97, 
         # NFL.com = 13
     "&scoring=", 13,
         # week 1 = 564, start at 563 + current week
     "&Segment=", 570)

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
