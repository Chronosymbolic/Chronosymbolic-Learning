(declare-rel inv (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (< x 2452) (inv x x)))

(rule (=> 
    (and 
        (inv x x)
        (= x1 (+ x 1))
    )
    (inv x1 x1)
  )
)

(rule (=> (and (inv x y) (not (= x y))) fail))

(query fail :print-certificate true)