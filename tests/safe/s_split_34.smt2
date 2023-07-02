(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 1)) (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (+ x0 y0))
        (= y1 (ite (and (> x1 -100) (< x1 100)) y0 (- y0))))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (not (and (>= x0 -100) (<= x0 100)))) fail))

(query fail)
