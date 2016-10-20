
home <- c(
    "Ben Roethlisberger",
    "Tyrod Taylor",
    "Jonathan Stewart",
    "Isaiah Crowell",
    "Alshon Jeffery",
    "Allen Robinson",
    "Tyrell Williams",
    "Zach Ertz",
    "Matt Forte",
    "Adam Vinatieri",
    "Bills"
)

away <- c(
    "David Johnson",
    "Larry Fitzgerald",
    "Michael Floyd",
    "John Brown",
    "Chandler Catanzaro",
    "Cardinals"
)

start_game <- function(home, away) {
    
    h <- proj %>%
        filter(Name %in% home) %>% 
        mutate(Team = "LOLBAYES") %>% 
        drop_na(wk_md)
    
    a <- proj %>%
        filter(Name %in% away) %>% 
        mutate(Team = "BillNyeMoneyballExtraordinaire") %>% 
        drop_na(wk_md) %>% 
        filter(wk_md > 1)
    
    match <- bind_rows(h, a) %>% 
        group_by(Team) %>% 
        summarise(
            wk_lo = sum(wk_lo),
            wk_md = sum(wk_md),
            wk_hi = sum(wk_hi))
    
    ggplot(data = match, aes(x = Team)) + 
        geom_pointrange(aes(y = wk_md, ymin = wk_lo, ymax = wk_hi)) + 
        geom_text(aes(y = wk_lo, label = round(wk_lo,0)), vjust = 2) + 
        geom_label(aes(y = wk_md, label = round(wk_md,0))) + 
        geom_text(aes(y = wk_hi, label = round(wk_hi,0)), vjust = -1) + 
        scale_y_sqrt() + 
        labs(title = "Game Center", x = "", y = "Fantasy Points") + 
        theme_minimal()
}

start_game(home, away)