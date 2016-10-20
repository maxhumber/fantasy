library(tidyverse)
library(rvest)
library(stringr)

# espn
# http://games.espn.com/ffl/tools/projections?&scoringPeriodId=5&seasonId=2016

week <- 7
position <- 2

url <- str_c(sep = "", 
    "http://games.espn.com/ffl/tools/projections?",
    "&scoringPeriodId=", week, 
    "&seasonId=2016",
    "&slotCategoryId=", position)

page <- read_html(url)

df <- page %>% 
    html_node("#playertable_0") %>% 
    html_table()


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