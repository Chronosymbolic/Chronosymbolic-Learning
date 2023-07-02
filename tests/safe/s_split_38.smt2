(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 50000) (= y0 0)) (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (ite (>= y0 x0) (+ x0 5) x0))
        (= y1 (ite (>= y0 x0) y0 (+ y0 1))))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (> y0 50000)
    (not (<= (- x0 y0) 5))) fail))

(query fail)

