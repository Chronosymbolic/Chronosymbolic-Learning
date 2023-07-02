(declare-rel inv (Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var z Int)
(declare-var x1 Int)
(declare-var y1 Int)
(declare-var z1 Int)

(declare-rel err ())

(rule (inv 0 0 0))

(rule (=> 
    (and 
        (inv x y z)
        (< x 100)
        (= x1 (+ x y))
        (= y1 (+ z 1))
        (= z1 (- y 1))
    )
    (inv x1 y1 z1)
  )
)

(rule (=> (and (inv x y z) (not (>= x 0))) err))

(query err)
