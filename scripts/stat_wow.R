library(tidyverse)
library(stringr)

# load data
nfl <- read_csv("data/nfl_df.csv") %>% mutate(source = "nfl")
sharks <- read_csv("data/sharks_df.csv") %>% mutate(source = "fantasy sharks")

# current week
nfl_week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

# combine
df <- bind_rows(nfl, sharks)

# compare function
compare_wow <- function(compare) { 
    
    df %>% 
        filter(name %in% compare) %>% 
        group_by(position, name, week) %>% 
        summarise(
            points_lo = min(points),
            points_me = mean(points),
            points_hi = max(points)) %>% 
        ggplot(aes(x = week, y = points_me)) + 
        geom_ribbon(aes(fill = name, ymin = points_lo, ymax = points_hi), alpha = 0.5) + 
        geom_line(aes(color = name), size = 1) + 
        geom_point(shape = 1, color = "white", size = 2) + 
        scale_x_continuous(breaks = seq(nfl_week, 17, 1)) + 
        theme_minimal()
}

# test
compare_wow(c("Dion Lewis", "Corey Coleman", "Jacquizz Rodgers"))
