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

params <- tibble(
    
    home = c(
        "Tyrod Taylor", 
        "Andy Dalton",
        "Buffalo Bills"),

    away = c(
        "Eli Manning", 
        "Alex Smith",
        "Chris Ivory")
)

params %>% pmap(proj_boot)

home %>% map_dbl(proj_boot) %>% sum()
away %>% map_dbl(proj_boot) %>% sum()



h_values <- h_values %>% as.data.frame() %>% as.bayesboot()
a_values <- a_values %>% as.data.frame() %>% as.bayesboot()
diff <- as.bayesboot(h_values - a_values)
plot(diff, compVal = 0)

plot(h_values)
plot(a_values)