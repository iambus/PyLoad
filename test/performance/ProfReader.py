import pstats
p = pstats.Stats("x.prof")
p.sort_stats("time").print_stats()
