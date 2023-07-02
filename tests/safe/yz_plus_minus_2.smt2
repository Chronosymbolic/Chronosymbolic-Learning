(declare-rel inv (Int Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var z Int)
(declare-var w Int)
(declare-var x1 Int)
(declare-var y1 Int)
(declare-var z1 Int)
(declare-var w1 Int)

(declare-rel err ())

(rule (inv 0 0 0 0))

(rule (=> 
    (and 
        (inv x y z w)
        (< x 10000)
        (= x1 (+ x w))
        (= y1 (+ z 1))
        (= z1 (- w 1))
        (= w1 (+ y 1))
    )
    (inv x1 y1 z1 w1)
  )
)

(rule (=> (and (inv x y z w) (not (>= x 0))) err))

(query err)
