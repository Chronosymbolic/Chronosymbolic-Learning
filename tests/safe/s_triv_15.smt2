(declare-rel inv (Bool Int))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= y 0) (= x (>= y 0))) (inv x y)))

(rule (=> 
    (and 
        (inv x y)
        (= y1 (- y 1))
    )
    (inv x y1)
  )
)

(rule (=> (and (inv x y) (not x)) fail))

(query fail :print-certificate true)