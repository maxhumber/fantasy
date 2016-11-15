library(tidyverse)

proj <- read_csv("data/proj.csv")

team <- c(
    "Jameis Winston",
    "Tyrod Taylor",
    "Ben Roethlisberger",
    "Jonathan Stewart",
    "Matt Forte",
    "Isaiah Crowell",
    "Allen Robinson",
    "Stefon Diggs",
    "Tyrell Williams",
    "Antonio Gates",
    "Dion Lewis",
    "Steve Smith",
    "Donte Moncrief",
    "Thomas Rawls",
    "Corey Coleman",
    "Justin Tucker",
    "Los Angeles Rams")

proj_team <- proj %>% 
    filter(name %in% team) %>%
    arrange(desc(mid)) %>% 
    mutate(rank = row_number())

proj_team %>% 
    ggplot(aes(x = rank, y = mid, color = position)) + 
    geom_linerange(aes(ymin = low, ymax = high)) +
    geom_label(aes(label = name), size = 2) + 
    scale_x_continuous(breaks = NULL) + 
    scale_y_continuous(breaks = seq(0, 30, 2)) + 
    theme_minimal() +
    theme(legend.position = "none") + 
    labs(y = "Fantasy Points", x = "")

proj_start <- function() { 
    
    pos_top <- function(pos = "QB", slots = 2) {
        p <- proj_team %>% 
            filter(position == pos) %>% 
            top_n(slots, wt = mid)
        return(p)
    }
    
    params <- tribble(
        ~pos, ~slots, 
        "QB", 2, 
        "WR", 3, 
        "RB", 2, 
        "TE", 1, 
        "K", 1,
        "DEF", 1
    )
    
    start <- params %>% 
        pmap(pos_top) %>% 
        bind_rows()
    
    flex <- proj_team %>% 
        anti_join(start, by = c("position", "name")) %>% 
        filter(position == "WR" | position == "RB") %>% 
        top_n(1, wt = mid)
    
    start <- start %>% 
        bind_rows(flex) %>% 
        select(position:high)
    
    return(start)
}

start <- proj_start()

knitr::kable(start)

write_csv(start, "data/proj_start.csv")
