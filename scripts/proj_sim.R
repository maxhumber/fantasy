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
    "Jacquizz Rodgers",
    "Jonathan Stewart",
    "Alshon Jeffery",
    "Tyrell Williams",
    "Allen Robinson",
    "Cameron Brate",
    "Nick Novak",
    "Detroit Lions")

away <- c(
    "Cam Newton",
    "Carson Palmer",
    "Theo Riddick",
    "Fozzy Whittaker",
    "A.J. Green",
    "Amari Cooper",
    "Cameron Meredith",
    "Tyler Eifert",
    "Jeremy Maclin")

hv <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    as.bayesboot()

plot(hv)

av <- replicate(1000, 
    home %>% 
    map_dbl(proj_boot) %>% 
    sum()) %>% 
    as.data.frame() %>% 
    as.bayesboot()

diff <- as.bayesboot(hv - av)
plot(diff, compVal = 0)
