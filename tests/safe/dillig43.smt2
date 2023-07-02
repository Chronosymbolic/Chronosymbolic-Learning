(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (and (= n y1) (not (= x1 y1))) (inv x1 y1 n)))

(rule (=> 
    (and 
        (inv x0 y0 n)
        (> x0 0)
        (= y1 (+ y0 x0))
    )
    (inv x0 y1 n)
  )
)

(rule (=> (and (inv x1 y1 n) (not (>= y1 n))) fail))

(query fail :print-certificate true)