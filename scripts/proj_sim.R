library(tidyverse)
library(bayesboot)

proj_all <- read_csv("data/proj_all.csv")

player <- "Tyrod Taylor"

proj_boot <- function(player) {
    
    p <- proj_all %>% 
        filter(name %in% player) %>% 
        sample_n(1, replace = TRUE) %>% 
        select(points) %>% 
        as.numeric()
    return(p)
}

proj_boot(player)

home <- c(
    "Tyrod Taylor", 
    "Andy Dalton",
    "Jacquizz Rodgers",
    "Buffalo Bills"
)

home %>% map_dbl(proj_boot) %>% sum()


h_values <- replicate(1000, sample_week(home))
a_values <- replicate(1000, sample_week(away))

h_values <- h_values %>% as.data.frame() %>% as.bayesboot()
a_values <- a_values %>% as.data.frame() %>% as.bayesboot()
diff <- as.bayesboot(h_values - a_values)
plot(diff, compVal = 0)

plot(h_values)
plot(a_values)