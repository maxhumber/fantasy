# flea
# http://www.fleaflicker.com/nfl/leaders?position=11&sortMode=7

pull_flea <- function(period = "week") {
    
    if ( period == "season" ){
        k <- 1
    } else {
        k <- 7
    }
    
    a <- data.frame()
    for ( i in c(4, 1, 2, 8, 16, 256) ) {
        url <- "http://www.fleaflicker.com/nfl/leaders?"
        for ( j in seq(0, 300, 20) ) {
            b <- read_html(paste0(url,"&position=",i,"&tableOffset=",j,"&sortMode=",k)) %>% 
                html_node("#table_0") %>% 
                html_table()
            a <- bind_rows(a, b)
        }
    }
    
    a_cols <- make.names(names = names(a), unique = TRUE, allow_ = TRUE)
    names(a) <- a_cols
    
    df <- a %>% 
        select(Player, Fantasy, Availability) %>% 
        drop_na(Player) %>% 
        filter(!(grepl("\\«|^Name", Player))) %>% 
        mutate(Pos = ifelse(grepl("\\sD\\/ST", Player), "DEF", NA)) %>% 
        mutate(Player = gsub("\\sD\\/ST.*","", Player)) %>%
        mutate(Player = ifelse(!is.na(Pos), gsub(".*\\s", "", Player), Player)) %>% 
        mutate(Status = ifelse(grepl("^Q", Player), "Q", NA)) %>%
        mutate(Status = ifelse(grepl("^IR", Player), "IR", Status)) %>% 
        mutate(Status = ifelse(grepl("^SUS", Player), "SUS", Status)) %>% 
        mutate(Status = ifelse(grepl("^OUT", Player), "OUT", Status)) %>%
        mutate(Player = gsub("^Q|^IR|^SUS|^OUT", "", Player)) %>% 
        mutate(Pos = ifelse(grepl("\\sQB", Player), "QB", Pos)) %>% 
        mutate(Pos = ifelse(grepl("\\sRB", Player), "RB", Pos)) %>% 
        mutate(Pos = ifelse(grepl("\\sWR", Player), "WR", Pos)) %>% 
        mutate(Pos = ifelse(grepl("\\sTE", Player), "TE", Pos)) %>% 
        mutate(Pos = ifelse(grepl("\\sK\\s", Player), "K", Pos)) %>% 
        mutate(Player = gsub("\\sQB.*|\\sRB.*|\\sWR.*|\\sTE.*|\\sK.*", "", Player)) %>% 
        filter(Availability != "% Own") %>% 
        mutate(Availability = gsub("\\%", "", Availability)) %>% 
        mutate(Availability = as.numeric(Availability)/100) %>% 
        mutate(Fantasy = as.numeric(Fantasy)) %>% 
        select(Pos, Name = Player, Flea = Fantasy, Availability, Status) %>% 
        arrange(desc(Flea))
    
    if ( k == 1 ) df$Flea <- df$Flea * 16
    
    return(df)
}