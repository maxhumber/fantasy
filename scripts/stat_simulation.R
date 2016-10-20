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

plot(h_values)
plot(a_values)