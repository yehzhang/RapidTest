from rapidtest import Test, Case

with Test('Solution.java') as t:
    Case('RDDRRD', result='Radiant')
    Case('R', result='Radiant')
    Case('D', result='Dire')
    Case('DRRDDR', result='Dire')
    Case('DDRDRR', result='Dire')
    Case('RRDRDD', result='Radiant')
    Case('RD', result='Radiant')
    Case('DR', result='Dire')
    Case('RR', result='Radiant')
    Case('DRR', result='Radiant')
