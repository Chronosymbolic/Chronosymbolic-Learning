## nonlin_mult_2.smt2.log
The log shows how we handle the instance in Example 1. 
- The "Information" section prints the statistics and the CHC system.
- The "Init Phase" section indicates that the reasoner finds an init safe zone from fact for inv: 
    ```
    And(Var_1 >= Var_0,
    Var_0 >= 1,
    Var_2 == 0,
    Var_4 == 0,
    Var_3 == 0),
    ```
  and an init unsafe zone from query for inv:
    `Not(Var_4 >= Var_0*Var_2)`
  Then, after a few iterations of expansion, the reasoner output initial safe/unsafe zones, which will incorporated in future hypothese. The process is light-weight which corresponds to line 6 `reason()` in Algorithm 1.
- The "Constraint Solving of Horn Clauses" section corresponds to line 5-15 in Algorithm 1. In this process, three positive samples `(1, 1, 3, 3, 3), (1, 1, 4, 4, 4), (1, 1, 5, 5, 5)` and 8 negative samples `(3, -3, -8, 3, -3), (3, -3, -9, 0, 0), (-1, -2, 5, -5, -2), (-1, -2, 4, -4, 0), (7, 3, -3, -8, -8), (7, 3, -4, -15, -11), (5, 4, 0, -2, 3), (5, 4, -1, -7, -1)` are discovered by implication cex converting (Lemma 3). The machine learning toolchain (SVMs and DT) is called multiple times to adjust the hypothesis during this section.
- In the second "Episode" (Epoch) of "Constraint Solving of Horn Clauses", all CHCs are passed `z3Check()`. This implies the satisfiability of the CHC system. The solution interpretations of all uninterpreted predicates are:
```
Relation: fail,
Candidate: False
13:20:06 - line:1308 -
Relation: inv,
Candidate: Or(And(Var_1 >= Var_0,
       Var_0 >= 1,
       Var_2 == 0,
       Var_4 == 0,
       Var_3 == 0),
   And(Var_0 >= 1,
       Var_2 == 1,
       Var_3 == Var_0,
       Var_4 == Var_1,
       Var_1 >= Var_0),
   And(Var_1 >= Var_0,
       Var_0 >= 1,
       Var_2 == 1,
       Var_4 + -1*Var_1 == 0,
       Var_3 + -1*Var_0 == 0),
   And(Var_0 >= 1,
       Var_2 == 2,
       Var_3 + -2*Var_0 == 0,
       Var_4 + -2*Var_1 == 0,
       Var_1 >= Var_0),
   And(Not(Or(Not(Var_4 >= Var_0*Var_2),
              Not(Var_4 + 3*Var_1 >= Var_0*(3 + Var_2)),
              Not(Var_4 + 2*Var_1 >= Var_0*(2 + Var_2)),
              Not(Var_4 + Var_1 >= Var_0*(1 + Var_2)))),
       Var_0 + -1*Var_1 <= 0))
```
