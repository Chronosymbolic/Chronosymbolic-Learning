(declare-rel inv1 (Int Int Int Int))
(declare-rel inv2 (Int Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)

; similar to s_mutants_06_m.smt2 but "slightly" more challenging

(declare-rel fail ())

(rule (=> (and (= x 0) (= y 0) (= i 0) (= j 0)) (inv1 x y i j)))

(rule (=> 
    (and 
        (inv1 x y i j)
        (= i1 (+ i 1))
        (= x1 (+ x i1))
        (= y1 (- y i1))
    )
    (inv1 x1 y1 i1 j)
  )
)

(rule (=> (inv1 x y i j) (inv2 x y i j)))

(rule (=>
    (and
        (inv2 x y i j)
        (= j1 (+ j 1))
        (= x1 (- x j1))
        (= y1 (+ y j1))
        )
    (inv2 x1 y1 i j1)
  )
)

(rule (=> (and (inv2 x y i j) (> i j) (not (> x y))) fail))

(query fail)
