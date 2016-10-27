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
    "Jameis Winston",
    "Matt Forte",
    "Jacquizz Rodgers",
    "Isaiah Crowell",
    "Stefon Diggs",
    "Tyrell Williams",
    "Allen Robinson",
    "Gary Barnidge",
    "Nick Novak",
    "Detroit Lions")

away <- c(
    "Cam Newton",
    "Carson Palmer",
    "Theo Riddick",
    "Darren Sproles",
    "A.J. Green",
    "Amari Cooper",
    "Davante Adams",
    "Tyler Eifert",
    "Jeremy Maclin", 
    "Cairo Santos",
    "Houston Texans")

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
