library(tidyverse)
library(rvest)
library(stringr)

# current week
nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

# pull nfl projection data
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
        rename(name = value)
    
    points <- page %>% 
        html_nodes("tbody") %>% 
        html_nodes("tr") %>% 
        html_nodes("td.stat.projected.numeric.last") %>% 
        html_text() %>% 
        as_tibble() %>% 
        rename(points = value)
    
    np <- bind_cols(name, points) %>% 
        mutate(week = week) %>% 
        mutate(position = position)
}

# function parameters 
params <- expand.grid(
    week = nfl_week:17,
    position = c(1, 2, 3, 4, 7, 8), 
    offset = seq(0, 300, 25)) %>% 
    filter(!(position %in% c(1, 4, 7, 8) & offset > 30))

# rest of season data pull
nfl_raw <- params %>% 
    pmap(pull_nfl) %>% 
    bind_rows()

# position look-up
pos_lookup <- tibble(
    position = c(1, 2, 3, 4, 7, 8),
    pos_real = c("QB", "RB", "WR", "TE", "K", "DEF")
)
   
# clean raw data
nfl_df <- nfl_raw %>% 
    left_join(pos_lookup, by = "position") %>% 
    select(position = pos_real, name, week, points) %>%
    filter(points != "-") %>% 
    mutate(points = as.numeric(points)) %>%
    mutate(name = str_replace(name, "\\-.*$", "")) %>% 
    mutate(name = str_replace(name, "\\sQB\\s|\\sRB\\s|\\sWR\\s|\\sTE\\s|\\sK\\s|\\DEF\\s", "")) %>% 
    mutate(name = str_replace(name, "\\sView Videos", "")) %>% 
    mutate(name = str_replace(name, "\\sView News", ""))

# week projections
nfl_week <- nfl_df %>% 
    filter(week == nfl_week)

# rest of season projections
nfl_ros <- nfl_df %>% 
    group_by(position, name) %>% 
    summarise(
        ros_total = sum(points),
        ros_mean = mean(points)) %>% 
    left_join(nfl_week, by = c("position", "name")) %>% 
    select(position:ros_mean, week_points = points) %>% 
    distinct(position, name, .keep_all = TRUE)

# save data
write_csv(nfl_df, "data/nfl_df.csv")
write_csv(nfl_ros, "data/nfl_ros.csv")
