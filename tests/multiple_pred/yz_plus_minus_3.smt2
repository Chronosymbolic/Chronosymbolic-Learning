(declare-rel inv1 (Int Int Int Int))
(declare-rel inv2 (Int Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var z Int)
(declare-var w Int)
(declare-var x1 Int)
(declare-var y1 Int)
(declare-var z1 Int)
(declare-var w1 Int)

(declare-rel err ())

(rule (inv1 0 0 0 0))

(rule (=> (inv1 x y z w) (inv2 x y z w)))

(rule (=> 
    (and 
        (inv2 x y z w)
        (< x 1000)
        (= x1 (+ x w))
        (= y1 (+ z 1))
        (= z1 (- w 1))
        (= w1 (+ y 1))
    )
    (inv2 x1 y1 z1 w1)
  )
)

(rule (=> (inv2 x y z w) (inv1 x y z w)))

(rule (=> (and (inv2 x y z w) (not (>= x 0))) err))

(query err)
