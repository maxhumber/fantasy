library(tidyverse)
library(rvest)
library(stringr)
library(curl)

# current week
nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

# pull fantasy sharks projection data
pull_sharks <- function(week = 1, position = 97) {
    
    url <- str_c(sep = "",
         "http://www.fantasysharks.com/apps/bert/forecasts/projections.php?", 
            # no league
         "League=-1",
             # QB + RB + WR + TE = 97
             # K - 7
             # DEF - 6
         "&Position=", position, 
             # NFL.com = 13
         "&scoring=", 13,
             # week 1 = 564, start at 563 + current week
         "&Segment=", 563 + week)
    
    page <- read_html(curl(url, handle = curl::new_handle("useragent" = "Mozilla/5.0")))
    
    name <- page %>% 
        html_nodes(".playerLink") %>% 
        html_text() %>% 
        as_tibble() %>% 
        rename(name = value)
    
    pos <- page %>% 
        html_nodes("#toolData td:nth-child(5)") %>% 
        html_text() %>% 
        as_tibble() %>% 
        rename(position = value)
    
        # 97 - points in 14 
        # 7 - points in 15
        # 6 - points in 12
    points_child <- ifelse(position == 97, 14, ifelse(position == 7, 15, 12)) 

    points <- page %>%
        html_nodes(str_c("td:nth-child(", points_child,")")) %>%
        html_text() %>% 
        as_tibble() %>% 
        rename(points = value)
    
    if (position == 97) {
        np <- bind_cols(pos, name, points) %>% 
            mutate(week = week)
    } else {
        np <- bind_cols(name, points) %>% 
            mutate(week = week, pos)
    }
    
}

# functional parameters
params <- expand.grid(
    week = nfl_week:17, 
    position = c(97, 7, 6)
)

test_offense <- pull_sharks(week = 17, position = 97)
test_k <- pull_sharks(week = 17, position = 7)
test_def <- pull_sharks(week = 17, position = 6)

test_all <- params %>% 
    pmap(pull_sharks) %>% 
    bind_rows()



