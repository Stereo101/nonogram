# nonogram
Nonogram solver written in python

Solves nonograms with this algorithm:
```
1. generate all legal permutations of square positions for each row/column
2. for each row and column, check all remaining permutations for squares that are either always filled, or always empty
3. mark these deterministic squares in the grid, and remove all permutations that disagree with that mark
4. if the grid became solved return True
5. if some row/col has no valid permutations left, the puzzle is impossible to solve from this state, return False
6. If step 3 added a new mark, goto step 2. If step 3 didn't add new marks: branch on a guess, goto step 2
```

This solves most smaller nonograms. For huge nonograms, the space requirement for each row/col can get out of hand: 

The recurrence relation for number of permutations in a given row is given by:
```
let r = len(A)
let f = row_width - sum(A)
where A is the row's nonogram sequence ie [1,1] or [2,1,1,4]
R(r,x) = 1 for x<=0
R(r,f) = sum from u = 0 to u = (f-r+2) for R(r-1,f-1-u)
```
This generates a variant of pascals triangle with the right side shaven off.

```
                                    1
                                  1    2
                                1    3    3
                              1    4    6    4
                            1    5   10   10    5
                          1    6   15   20   15    6
                        1    7   21   35   35   21    7
                      1    8   28   56   70   56   28    8
                    1    9   36   84  126  126   84   36    9
                  1   10   45  120  210  252  210  120   45   10
                1   11   55  165  330  462  462  330  165   55   11
              1   12   66  220  495  792  924  792  495  220   66   12
            1   13   78  286  715 1287 1716 1716 1287  715  286   78   13
          1   14   91  364 1001 2002 3003 3432 3003 2002 1001  364   91   14
        1   15  105  455 1365 3003 5005 6435 6435 5005 3003 1365  455  105   15
```
We can adjust the regular binomial calculation to account for this shaving:

```
let r = len(A)
let f = row_width - sum(A)
where A is the row's nonogram sequence ie [1,1] or [2,1,1,4]
R(r,f) = !(f+1) / (!r * !(f+1 -r))
```
Since `f = row_width - sum(A)` we have `O(!w)` number of permutations per row, which means for large grids, we'll have too many permutations to work through.
