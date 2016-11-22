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
<<<<<<< HEAD
    "Steve Smith",
    "Allen Robinson",
    "Corey Coleman",
    "Stefon Diggs",
    "Antonio Gates",
    "Justin Tucker",
=======
    #"Steve Smith",
    "Stefon Diggs",
    #"Corey Coleman",
    "Allen Robinson",
    "Antonio Gates",
    #"Justin Tucker",
>>>>>>> 2a5ca3214e6df686fc1ea5bff32e74e37252a17d
    "Los Angeles Rams")

away <- c(
    "Matt Ryan",
    "Carson Wentz",
    "DeMarco Murray", 
    "Devontae Booker",
<<<<<<< HEAD
    "Brandon Marshall", 
    "Terrelle Pryor", 
    "Odell Beckham", 
    "Jimmy Graham", 
    "Terrance West", 
    "Dustin Hopkins", 
=======
    #"Brandon Marshall", 
    "Terrelle Pryor", 
    "Odell Beckham", 
    "Jimmy Graham", 
    #"Terrance West", 
    "Chris Boswell", 
>>>>>>> 2a5ca3214e6df686fc1ea5bff32e74e37252a17d
    "Denver Broncos")

hv <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
<<<<<<< HEAD
    # mutate(`.` = `.` + 25.04) %>% 
=======
    mutate(`.` = `.` + 21.70) %>% 
>>>>>>> 2a5ca3214e6df686fc1ea5bff32e74e37252a17d
    as.bayesboot()

plot(hv)

av <- replicate(1000, 
    away %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
<<<<<<< HEAD
    # mutate(`.` = `.` + 27.00) %>% 
=======
    mutate(`.` = `.` + 12.50) %>% 
>>>>>>> 2a5ca3214e6df686fc1ea5bff32e74e37252a17d
    as.bayesboot()

plot(av)

diff <- as.bayesboot(hv - av)
plot(diff, compVal = 0)
