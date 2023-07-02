(declare-rel inv (Int Int Int))
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (> z1 0) (= x1 0) (= y1 1))
          (inv x1 y1 z1)))

(rule (=> 
    (and 
        (inv x0 y0 z0)
        (<= y0 z0)
        (= y1 (+ y0 1))
        (or (= x1 (+ x0 1)) (= x1 (- x0 1)))
    )
    (inv x1 y1 z0)
  )
)

(rule (=> (and (inv x1 y1 z1) (> y1 z1) (not (and (>= x1 (- z1)) (<= x1 z1)))) fail))

(query fail :print-certificate true)