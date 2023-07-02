(declare-rel inv (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (< x 2452) (inv x x)))

(rule (=> 
    (and 
        (inv x y)
        (= x1 (+ x 1))
    )
    (inv x1 y)
  )
)

(rule (=> (and (inv y y) (not (< y 2452))) fail))

(query fail :print-certificate true)