library(tidyverse)
library(rvest)
library(jsonlite)
library(stringr)

pull_nfl <- function(week = 1, position = 1, offset = 0) {
    
    url <- str_c(sep = "",
        "http://fantasy.nfl.com/research/projections?", 
            # 1 to 17
        "statType=weekProjectedStats&statWeek=", week,
            # QB - 1
            # RB - 2
            # WR - 3
            # TE - 4
            # K - 7
            # DEF - 8
        "&position=", position, 
            # increment by 25
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
    
    np <- bind_cols(name, points) %>% 
        mutate(week = week)
}

params <- expand.grid(
    week = 1:7,
    position = c(1, 2, 3, 4, 7, 8), 
    offset = seq(0, 300, 25)
)

historical <- params %>% 
    pmap(pull_nfl) %>% 
    bind_rows()


nfl <- bind_cols(name, points) %>% 
    str_extract(name, "\\sQB\\s")
    separate(
        Name, 
        into = c("Name", "Junk"), 
        sep = "\\sQB\\s|\\sRB\\s|\\sWR\\s|\\sTW\\s|\\sK\\s|\\DEF\\s") %>% 
    select(-Junk)
    


