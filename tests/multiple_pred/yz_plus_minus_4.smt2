(declare-rel inv1 (Int Int Int))
(declare-rel inv2 (Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var z Int)
(declare-var x1 Int)
(declare-var y1 Int)
(declare-var z1 Int)

(declare-rel err ())

(rule (inv1 0 0 0))

(rule (=> (inv1 x y z) (inv2 x y z)))

(rule (=> 
    (and 
        (inv2 x y z)
        (< x 100)
        (= x1 (+ x y))
        (= y1 (+ z 1))
        (= z1 (- y 1))
    )
    (inv2 x1 y1 z1)
  )
)

(rule (=> (inv2 x y z) (inv1 x y z)))

(rule (=> (and (inv1 x y z) (not (>= x 0))) err))

(query err)
