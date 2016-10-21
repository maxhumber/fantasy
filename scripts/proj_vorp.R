library(tidyverse)

proj <- read_csv("data/proj.csv")
proj_start <- read_csv("data/proj_start.csv")

params <- tribble(
    ~pos, ~slots,
    "QB", 20,
    "WR", 35, 
    "RB", 25, 
    "TE", 10, 
    "K", 10,
    "DEF", 10
)

replacement_player <- function(pos, slots) {
    rp <- proj %>% 
        filter(position == pos) %>% 
        arrange(desc(mid)) %>% 
        filter(row_number() <= slots) %>% 
        group_by(position) %>% 
        summarise(rp = mean(mid))
}

rp <- params %>% 
    pmap(replacement_player) %>% 
    bind_rows()

proj_vorp <- proj %>% 
    left_join(rp, by = "position") %>% 
    mutate(vorp = mid - rp) %>% 
    select(position, name, vorp) %>% 
    arrange(desc(vorp))

start_vorp <- proj_start %>% 
    left_join(rp, by = "position") %>% 
    mutate(vorp = mid - rp) %>% 
    distinct(.keep_all = TRUE)