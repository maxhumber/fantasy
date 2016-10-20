library(tidyverse)
library(stringr)

nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

ros <- read_csv("data/ros.csv")

proj_wow <- function(players) { 
    
    ros %>% 
        filter(name %in% players) %>% 
        ggplot(aes(x = week, y = mid)) + 
        geom_ribbon(aes(fill = name, ymin = low, ymax = high), alpha = 0.5) + 
        geom_line(aes(color = name), size = 1) + 
        geom_point(shape = 1, color = "white", size = 2) + 
        scale_x_continuous(breaks = seq(nfl_week, 17, 1)) + 
        theme_minimal() + 
        labs(title = "Players ROS", x = "Week", y = "Fantasy Points")
}

# test
proj_wow(c("Alex Smith", "Ben Roethlisberger"))
proj_wow(c("Alex Smith", "Andy Dalton", "Tyrod Taylor"))

proj_wow(c("Jameis Winston", "Ben Roethlisberger"))

ros_mean <- ros %>% 
    group_by(position, name) %>% 
    summarise(ros_mean = mean(mid))
