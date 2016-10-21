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
    "Tyrod Taylor", 
    "Andy Dalton",
    "Matt Forte",
    "Isaiah Crowell",
    "Kenny Britt",
    "Alshon Jeffery",
    "Allen Robinson",
    "Zach Ertz",
    "Jacquizz Rodgers",
    "Adam Vinateri",
    "Buffalo Bills")

away <- c(
    "Eli Manning", 
    "Alex Smith",
    "Chris Ivory")

hv <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    as.bayesboot()

av <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    as.bayesboot()

diff <- as.bayesboot(hv - av)
plot(diff, compVal = 0)
