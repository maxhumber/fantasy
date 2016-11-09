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
    "Jonathan Stewart",
    "Steve Smith",
    "Allen Robinson",
    "Corey Coleman",
    "Stefon Diggs",
    "Antonio Gates",
    "Justin Tucker",
    "Los Angeles Rams")

away <- c(
    "Matt Ryan",
    "Carson Wentz",
    "DeMarco Murray", 
    "Devontae Booker",
    "Brandon Marshall", 
    "Terrelle Pryor", 
    "Odell Beckham", 
    "Jimmy Graham", 
    "Terrance West", 
    "Dustin Hopkins", 
    "Denver Broncos")

hv <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    # mutate(`.` = `.` + 25.04) %>% 
    as.bayesboot()

plot(hv)

av <- replicate(1000, 
    away %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    # mutate(`.` = `.` + 27.00) %>% 
    as.bayesboot()

plot(av)

diff <- as.bayesboot(hv - av)
plot(diff, compVal = 0)
