(declare-rel inv (Bool Int))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and x (= x (= y 0))) (inv x y)))

(rule (=> 
    (and 
        (inv x y)
        (= y1 (+ y 1))
    )
    (inv x1 y1)
  )
)

(rule (=> (and (inv x y) (not (>= y 0))) fail))

(query fail :print-certificate true)