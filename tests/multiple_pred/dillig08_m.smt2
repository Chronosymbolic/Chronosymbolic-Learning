(declare-rel inv (Int Int))
(declare-rel inv1 (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 0) ) (inv1 x0 y0)))

(rule (=> (and (inv1 x0 y0 ) (= y1 (+ y0 1))) (inv1 x0 y1 )))

(rule (=> (inv1 x0 y0 ) (inv x0 y0 )))

(rule (=> 
    (and 
        (inv x0 y0)
        (or 
            (and (= x1 (+ x0 1)) (= y1 (+ y0 100)))
            (and (= x1 x0) (= y1 y0))
            (and 
                 (= x1 (ite (>= x0 4) (+ x0 1) x0))
                 (= y1 (ite (>= x0 4) (+ y0 1) (ite (< x0 0) (- y0 1) y0)))
            )
        )
    )
    (inv x1 y1)
  )
)

(rule (=> (and (inv x1 y1) (not (< x1 4)) (not (> y1 2))) fail))

(query fail)
