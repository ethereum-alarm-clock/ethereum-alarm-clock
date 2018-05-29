set.seed(123)

tx_cost <- function(A_x, n, C_tx) {
  (1 - A_x) * (n - 1) * C_tx
}

bounty <- function(timebounty, C_c, n) {
  (timebounty - C_c) / n
}

P_s <- function(P_mod, timebounty, C_c, n, A_x, C_tx) {
  P_mod * bounty(timebounty, C_c, n) - tx_cost(A_x, n, C_tx)
}

P_f <- function(C_c, deposit) {
  -C_c - deposit
}

P_nf <- function(timebounty, deposit, n, A_x, C_tx) {
  (timebounty + deposit) / n - tx_cost(A_x, n, C_tx)
}

outcome <- function(p_ld,
                    A_x,
                    n,
                    C_tx,
                    P_mod,
                    timebounty,
                    C_c,
                    deposit) {
  P_s(P_mod, timebounty, C_c, n, A_x, C_tx) * (1 - p_ld) + (P_f(C_c, deposit) + P_nf(timebounty, deposit, n, A_x, C_tx)) * p_ld
}

#Normal distrubutions
timebounties = rnorm(1:1000, mean = 300000, sd = 50000)
deposits = rnorm(1:1000, mean = 600000, sd = 50000)

network = rnorm(1:1000, mean = 8, sd = 2)
network = as.integer(network)
network[network <= 0] = 1

accs = rnorm(1:1000, mean = 0.95, sd = 0.05)
accs[accs > 1] = 1

p_lds = rnorm(1:1000, mean = 0.02, sd = 0.01)
p_lds[p_lds < 0] = 0

c_c = 90000 #claiming cost
c_tx = 25000 #failing tx cost

p_mods = seq(0, 1, 0.05) #payment modifiers

simulate <- function() {
  result = c()
  
  p_mods = seq(0, 1, 0.05)
  for (p_mod in p_mods) {
    out = c()
    for (i in 1:10000) {
      A_x = sample(accs, 1)
      p_ld = sample(p_lds, 1)
      n = sample(network, 1)
      deposit = sample(deposits, 1)
      timebounty = sample(timebounties, 1)
      
      out[i] = outcome(p_ld,
                       A_x,
                       n,
                       c_tx,
                       p_mod,
                       timebounty,
                       c_c,
                       deposit)
    }
    result <- c(result, mean(out))
  }
  
  result
}

results = simulate()
target_gas = 1000000

x = data.frame(p_mod = p_mods, res = results, tx = as.integer(target_gas / results))
subset(x, res > 0)