library(tidyverse)
library(rvest)
library(stringr)

# espn
# http://games.espn.com/ffl/tools/projections?&scoringPeriodId=5&seasonId=2016

nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

pull_espn <- function(week, position = 0, offset = 0) { 

    url <- str_c(sep = "", 
        "http://games.espn.com/ffl/tools/projections?",
        "&scoringPeriodId=", week, 
        "&seasonId=2016",
        "&slotCategoryId=", position,
        "&startIndex=", offset)
    
    page <- read_html(url)
    
    df <- page %>% 
        html_node("#playertable_0") %>% 
        html_table()
}

# functional parameters
params <- expand.grid(
    week = nfl_week,
    position = c(0, 2, 4, 6, 16, 17),
    offset = seq(0, 320, 40)) %>% 
    filter(!(position %in% c(0, 6, 16, 17) & offset > 40))

# espn pull
espn_raw <- params %>% 
    pmap(pull_espn) %>% 
    bind_rows()

# clean data
espn_clean <- espn_raw %>% 
    mutate(PLAYERS = ifelse(is.na(PLAYERS), `DEFENSIVE PLAYERS`, PLAYERS)) %>% 
    select(name = PLAYERS, points = TOTAL) %>% 
    mutate(points = parse_number(points)) %>% 
    drop_na() %>% 
    mutate(week = nfl_week)


        mutate(A = gsub("D\\/ST\\sD\\/ST|\\*$","",A)) %>% 
        separate(B, into = c("Fill", "Team", "Pos"), sep = "\\s", extra = "drop") %>% 
        mutate(Pos = ifelse(is.na(Pos), "DEF", Pos)) %>% 
        mutate(A = ifelse(Pos == "DEF", gsub("\\s.*", "", A), A)) %>% 
        mutate(TOTAL = as.numeric(TOTAL)) %>% 
        distinct(.keep_all = TRUE) %>% 
        arrange(desc(TOTAL)) %>% 
        select(Pos, Name = A, ESPN = TOTAL)
  