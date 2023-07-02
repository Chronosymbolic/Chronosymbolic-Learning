(declare-rel inv (Int Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var z Int)
(declare-var z1 Int)

(declare-var i Int)
(declare-var i1 Int)

(declare-rel fail ())

(rule (=> (and (> y 0) (= z 1) (> x 0) (>= i x)) (inv x y z i)))

(rule (=> 
    (and 
        (inv x y z i)
        (> x 0)
        (= x1 (- x y))
        (= y1 (- y z))
        (= z1 (- z))
        (= i1 (- i 1))
    )
    (inv x1 y1 z1 i1)
  )
)

(rule (=> (and (inv x y z i) (> x 0) (< i 0)) fail))

(query fail :print-certificate true)
