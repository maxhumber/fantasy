# fantasy_scrape.R

# TO DO
# http://www.fftoday.com/rankings/playerwkproj.php?Season=2016&GameWeek=4&PosID=20&LeagueID=1

# packages

library(tidyverse)
library(rvest)
library(jsonlite)
library(magrittr)
library(bayesboot)

# init

week <- ceiling(as.numeric(Sys.Date() - as.Date("2016-09-05")) / 7 )

# sharks
# http://www.fantasysharks.com/apps/Projections/WeeklyProjections.php?pos=ALL&format=json

pull_sharks <- function(period = "week") {
    
    if ( period == "season" ){
        k <- "SeasonProjections.php?"
    } else {
        k <- "WeeklyProjections.php?"
    }
    
    Pos <- c("QB", "RB", "WR", "TE", "PK", "D")
    a <- data.frame()
    
    for ( i in Pos ) {
        url <- "http://www.fantasysharks.com/apps/Projections/"
        b <- fromJSON(paste0(url,k,"pos=",i,"&format=json"))
        b$Pos <- i
        a <- bind_rows(a, b) 
    }
    
    df <- a %>% 
        mutate(Pos = ifelse(Pos == "PK", "K", Pos)) %>% 
        mutate(Pos = ifelse(Pos == "D", "DEF", Pos)) %>% 
        separate(Name, into = c("last", "first"), sep = ",", extra = "drop") %>% 
        mutate(Name = paste0(first," ",last)) %>% 
        mutate(Name = gsub("^\\s", "", Name)) %>% 
        select(Pos, Name, Sharks = FantasyPoints) %>% 
        mutate(Name = ifelse(Pos == "DEF", gsub(".*\\s", "", Name), Name)) %>% 
        arrange(desc(Sharks))
    
    return(df)
}

# sharks <- pull_sharks()

# espn
# http://games.espn.com/ffl/tools/projections?&scoringPeriodId=5&seasonId=2016

pull_espn <- function(period = "week") {
    
    options(warn = -1)
    
    if ( period == "season" ){
        k <- "true"
    } else {
        k <- "false"
    }
    
    a <- data.frame()
    for ( i in c(0, 2, 4, 6, 16, 7) ) {
        url <- "http://games.espn.com/ffl/tools/projections?&seasonId=2016"
        for ( j in seq(0, 200, 40) ) {
            b <- read_html(paste0(url,"&slotCategoryId=",i,"&startIndex=",j,"&seasonTotals=",k)) %>% 
                html_node("#playertable_0") %>% 
                html_table()
            a <- rbind(a, b)
        }
    }
    
    if ( k == "true" ) a[,1] <- NULL
    
    a_cols <- make.names(names = names(a), unique = TRUE, allow_ = TRUE)
    names(a) <- a_cols
    
    df <- a %>% 
        filter(PLAYERS != "PLAYER, TEAM POS") %>% 
        select(PLAYERS, TOTAL) %>% 
        separate(PLAYERS, into = c("A", "B"), sep = ",", extra = "drop") %>% 
        filter(grepl("[0-9]{1,2}",TOTAL)) %>% 
        mutate(A = gsub("D\\/ST\\sD\\/ST|\\*$","",A)) %>% 
        separate(B, into = c("Fill", "Team", "Pos"), sep = "\\s", extra = "drop") %>% 
        mutate(Pos = ifelse(is.na(Pos), "DEF", Pos)) %>% 
        mutate(A = ifelse(Pos == "DEF", gsub("\\s.*", "", A), A)) %>% 
        mutate(TOTAL = as.numeric(TOTAL)) %>% 
        distinct(.keep_all = TRUE) %>% 
        arrange(desc(TOTAL)) %>% 
        select(Pos, Name = A, ESPN = TOTAL)
    
    options(warn = 0)
    
    return(df)
}

# espn <- pull_espn()

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

# flea <- pull_flea()

# pros
# https://www.fantasypros.com/nfl/projections/qb.php?

pull_pros <- function(period = "week") {
    
    if ( period == "season" ){
        j <- "?week=draft"
    } else {
        j <- NULL
    }
    
    a <- data.frame()
    for ( i in c("qb", "rb", "wr", "te", "k", "dst") ) {
        b <- read_html(paste0("https://www.fantasypros.com/nfl/projections/",i,".php", j)) %>% 
            html_nodes("#data td , .tablesorter-header") %>% 
            html_text()
        
        if ( i == "qb") {
            Player <- b[seq(5, 1200, 11)]
            Pros <- b[seq(15, 1210, 11)]
        } else if ( i == "rb" | i == "wr") {
            Player <- b[seq(5, 1200, 9)]
            Pros <- b[seq(13, 1205, 9)]
        } else if ( i == "te" ) {
            Player <- b[seq(4, 1200, 6)]
            Pros <- b[seq(9, 1205, 6)]
        } else if ( i == "k" ) {
            Player <- b[seq(1, 1200, 5)]
            Pros <- b[seq(5, 1200, 5)]
        } else if ( i == "dst" ) { 
            Player <- b[seq(1, 1200, 11)]
            Pros <- b[seq(11, 1210, 11)]
        }
        
        b <- data.frame(Player = Player, Pros = Pros)
        b$Pos <- toupper(i)
        
        a <- bind_rows(a, b)
        
        df <- a %>% 
            drop_na(Player) %>% 
            mutate(Pos = ifelse(Pos == "DST", "DEF", Pos)) %>% 
            separate(Player, into = c("A", "B", "C"), sep = "\\s", extra = "drop", fill = "left") %>% 
            mutate(C = ifelse(Pos == "DEF" & C == "", B, C)) %>% 
            mutate(Player = paste(A, B)) %>% 
            mutate(Player = ifelse(Pos == "DEF", C, Player)) %>% 
            mutate(Pros = as.numeric(Pros)) %>% 
            select(Pos, Name = Player, Pros) %>% 
            arrange(desc(Pros))
    }
    return(df)
}

# pros <- pull_pros() 

# week data

espn <- pull_espn()
flea <- pull_flea()
pros <- pull_pros()
sharks <- pull_sharks()

week <- espn %>%
    full_join(flea) %>% 
    full_join(sharks) %>% 
    full_join(pros)

# season data

espn.s <- pull_espn(period = "season")
flea.s <- pull_flea(period = "season")
pros.s <- pull_pros(period = "season")
sharks.s <- pull_sharks(period = "season")

season <- espn.s %>%
    full_join(flea.s) %>% 
    full_join(sharks.s) %>% 
    full_join(pros.s)

rm(espn, espn.s, flea, flea.s, pros, pros.s)
rm(sharks, sharks.s)

# clean 

proj.wk <- week %>% 
    gather(Source, Points, -Pos, -Name, -Availability, -Status) %>% 
    group_by(Pos, Name, Availability, Status) %>% 
    summarise(
        wk_lo = min(Points, na.rm = TRUE),
        wk_md = mean(Points, na.rm = TRUE),
        wk_hi = max(Points, na.rm = TRUE)
    )

proj.se <- season %>% 
    select(-Availability, -Status) %>% 
    gather(Source, Points, -Pos, -Name) %>% 
    group_by(Pos, Name) %>% 
    summarise(
        se_lo = min(Points, na.rm = TRUE),
        se_md = mean(Points, na.rm = TRUE),
        se_hi = max(Points, na.rm = TRUE)
    )

# join everything

proj <- full_join(proj.wk, proj.se) %>% 
    mutate(overunder = wk_md - se_md/16) %>% 
    ungroup() %>% 
    as.data.frame()

# team management analysis

roster <- c(
    "Andy Dalton",
    "Ben Roethlisberger",
    "Tyrod Taylor",
    "Matt Forte",
    "Isaiah Crowell",
    "Allen Robinson",
    "Tyrell Williams",
    "Sterling Shepard",
    "Zach Ertz",
    "Titans",
    "Jonathan Stewart",
    "Chris Ivory",
    "Bilal Powell",
    "Sammie Coates",
    "Alshon Jeffery")

start_bench <- function(roster) {
    
    team <- proj %>%
        filter(Name %in% roster) %>% 
        ungroup() %>% 
        arrange(desc(wk_md)) %>% 
        mutate(rank = row_number())
    
    team %>% 
        ggplot(aes(x = rank, y = wk_md, color = Pos)) + 
        geom_pointrange(aes(ymin = wk_lo, ymax = wk_hi)) + 
        geom_label(aes(label = Name), size = 2) + 
        theme_minimal() + 
        labs(title = "BFL Week Projections", y = "Points", x = "Rank Order") + 
        theme(legend.position = "none")
    
}

start_bench(roster)
        
# waiver target list

targets <- proj %>% 
    mutate(Team = ifelse(Name %in% roster, "Yes", "")) %>%
    filter(wk_md > 0) %>% 
    arrange(desc(wk_md))
    
start_comparison <- function(playerX, playerY) {
    targets %>% 
        filter(Name %in% c(playerX, playerY)) %>% 
        ggplot(aes(x = Name)) + 
        geom_pointrange(aes(y = wk_md, ymin = wk_lo, ymax = wk_hi), color = "red") + 
        geom_pointrange(aes(y = se_md, ymin = se_lo, ymax = se_hi), color = "black") +
        geom_text(aes(y = wk_lo, label = round(wk_lo,1)), color = "red", vjust = 2) + 
        geom_label(aes(y = wk_md, label = round(wk_md,1)), color = "red") + 
        geom_text(aes(y = wk_hi, label = round(wk_hi,1)), color = "red", vjust = -1) + 
        geom_label(aes(y = se_md, label = round(se_md,1)), color = "black") + 
        scale_y_sqrt() + 
        labs(title = "Player Comparison", x = "", y = "Fantasy Points") + 
        theme_minimal()
}

start_comparison("Sammie Coates", "Tyrell Williams")

# VS Game Centre Projections

home <- c(
    "Ben Roethlisberger",
    "Andrew Luck",
    "Matt Forte",
    "Isaiah Crowell",
    "Steve Smith",
    "Alshon Jeffery",
    "Sammie Coates",
    "Zach Ertz",
    "Sterling Shepard",
    "Mike Nugent",
    "Panthers"
)

away <- c(
    "Ryan Tannehill",
    "Derek Carr",
    "C.J. Anderson",
    "Melvin Gordon",
    "Jordy Nelson",
    "Michael Crabtree",
    "Emmanuel Sanders",
    "Rob Gronkowski",
    "Travis Benjamin",
    "Chris Boswell",
    "Patriots"
)

start_game <- function(home, away) {
    
    h <- proj %>%
        filter(Name %in% home) %>% 
        mutate(Team = "LOLMONDAY")
    
    a <- proj %>%
        filter(Name %in% away) %>% 
        mutate(Team = "Away")
    
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

# game probabilities

week.t <- week %>% 
    gather(Source, Points, -Pos, -Name, -Availability, -Status) %>% 
    drop_na(Points)

sample_week <- function(players){
    total <- 0
    for (i in players) {
        
        v <- week.t %>% 
            filter(Name == i) %>% 
            sample_n(1, replace = TRUE) %>% 
            select(Points) %>% 
            as.numeric()
        
        total <- total + v
    }
    return(total)
}
    
h_values <- replicate(1000, sample_week(home))
a_values <- replicate(1000, sample_week(away))

h_values <- h_values %>% as.data.frame() %>% as.bayesboot()
a_values <- a_values %>% as.data.frame() %>% as.bayesboot()
diff <- as.bayesboot(h_values - a_values)
plot(diff, compVal = 0)

hist(h_values)
hist(a_values)

