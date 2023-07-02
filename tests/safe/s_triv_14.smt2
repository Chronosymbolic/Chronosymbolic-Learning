(declare-rel inv (Bool Int))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (= y 0) (inv x y)))

(rule (=> 
    (and 
        (inv x y)
        (= x1 (= (mod y 2) 0))
        (= y1 (ite x1 (+ y 2) (- y 1)))
    )
    (inv x1 y1)
  )
)

(rule (=> (and (inv x y) (= y 13621)) fail))

(query fail :print-certificate true)