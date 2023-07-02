(declare-rel inv (Int Int))
(declare-rel inv1 (Int Int))
(declare-rel inv2 (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= y 0)) (inv x y)))

(rule (=> 
    (and 
        (inv x y)
        (= x1 (+ x 1))
        (= y1 (- y 1))
    )
    (inv x1 y1)
  )
)

(rule (=> (and (inv x y) (> x 0)) (inv1 x y)))

(rule (=>
    (and
        (inv1 x y)
        (= x1 (- x 1))
        (= y1 (+ y 1))
    )
    (inv1 x1 y1)
  )
)

(rule (=> (and (inv1 x y) (= y 0)) (inv2 x y)))

(rule (=>
    (and
        (inv2 x y)
        (= x1 (+ x 1))
        (= y1 (+ y 1))
    )
    (inv2 x1 y1)
  )
)

(rule (=> (and (inv2 x y) (not (= x y))) fail))

(query fail)

