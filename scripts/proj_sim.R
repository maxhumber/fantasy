library(tidyverse)
library(bayesboot)

proj_all <- read_csv("data/proj_all.csv")

proj_boot <- function(player) {
    
    p <- proj_all %>% 
        filter(name %in% player) %>% 
        sample_n(1, replace = TRUE) %>% 
        select(points) %>% 
        as.numeric()
    return(p)
}
    
home <- c(
    "Ben Roethlisberger", 
    "Jameis Winston",
    "Matt Forte",
    "Isaiah Crowell",
    "Allen Robinson",
    "Stefon Diggs",
    "Tyrell Williams",
    "Jonathan Stewart",
    "Gary Barnidge",
    "Blair Walsh",
    "Carolina Panthers")

away <- c(
    "Joe Flacco",
    "Philip Rivers",
    "Ezekiel Elliott",
    "Jalen Richard",
    "Tavon Austin",
    "Mike Evans",
    "Jordan Matthews",
    "Hunter Henry",
    "DeAngelo Williams", 
    "Josh Lambo",
    "Philadelphia Eagles")

hv <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    as.bayesboot()

plot(hv)

av <- replicate(1000, 
    away %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    as.bayesboot()

plot(av)

diff <- as.bayesboot(hv - av)
plot(diff, compVal = 0)
