(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 0) (distinct z0 0)) (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ x0 1))
        (= y1 (ite (> z0 0) (+ y0 1) (- y0 2)))
        (= z1 (ite (= x0 100) (- z0) z0)))
    (inv x1 y1 z1)))

(rule (=> (and (inv x0 y0 z0) (= x0 200)
    (not (<= y0 0))) fail))

(query fail)

