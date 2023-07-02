(declare-rel inv (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (inv 0 0))

(rule (=> 
    (and 
        (inv x y)
        (= x1 (+ x y))
    )
    (inv x1 y)
  )
)

(rule (=> (and (inv x 0) (> x 25) (not (= x y))) fail))

(query fail :print-certificate true)