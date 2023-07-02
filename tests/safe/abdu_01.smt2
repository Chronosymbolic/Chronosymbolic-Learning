(declare-rel inv (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var len Int)

(declare-rel fail ())

(rule (=>
    (and (= x 0) (= y 0) (>= len 0)) (inv x y len)
  )
)

(rule (=> 
    (and 
	(inv x y len)
        (< x len)
	(= x1 (+ x 1))
	(= y1 (+ y 2))
    )
    (inv x1 y1 len)
  )
)

(rule (=> (and (inv x y len) (not (= y (* 2 x)))) fail))

(query fail :print-certificate true)

