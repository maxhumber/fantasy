library(tidyverse)
library(stringr)

nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

ros <- read_csv("data/ros.csv") %>% 
    group_by(position, name) %>% 
    complete(week = seq(nfl_week, 17, 1))

rp <- ros %>% 
    group_by(position, week) %>% 
    mutate(slot = row_number(desc(mid))) %>% 
    filter(
        (position == "QB"  & slot <= 20) |
        (position == "WR"  & slot <= 35) |
        (position == "RB"  & slot <= 25) |
        (position == "TE"  & slot <= 10) |
        (position == "K"   & slot <= 10) |
        (position == "DEF" & slot <= 10)) %>% 
    group_by(position, week) %>% 
    summarise(
        rp = mean(mid))

vorp <- ros %>% 
    left_join(rp, by = c("position", "week")) %>% 
    mutate(vorp = mid - rp)

proj_wow <- function(players) { 
    
    vorp %>% 
        filter(name %in% players) %>% 
        ggplot(aes(x = week, y = vorp)) + 
        annotate("rect", xmin = -Inf, xmax = Inf, ymin = 0, ymax = Inf, fill = "green", alpha = 1/10) + 
        annotate("rect", xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = 0, fill = "red", alpha = 1/10) + 
        geom_line(aes(color = name), size = 2) + 
        geom_point(aes(size = sd, fill = name), shape = 21, color = "white", show.legend = FALSE) + 
        scale_x_continuous(breaks = seq(nfl_week, 17, 1)) + 
        theme_minimal() + 
        labs(title = "ROS VORP", x = "Week", y = "Value Over Replacement") + 
        theme(panel.grid.minor.x = element_blank())
}

# test
proj_wow(c("Steve Smith", "Jonathan Stewart"))

