(declare-rel inv (Int Int Int Int))
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (=> (and (= z1 x1) (= y1 w1)) (inv x1 y1 z1 w1)))

(rule (=> 
    (and 
        (inv x0 y0 z0 w0)
        (not (= x0 0))
        (= x1 (- x0 1))
        (= y1 (- y0 1))
    )
    (inv x1 y1 z0 w0)
  )
)

(rule (=> (and (inv x1 y1 z1 w1) (= x1 0) (= z1 w1) (not (= y1 0))) fail))

(query fail :print-certificate true)