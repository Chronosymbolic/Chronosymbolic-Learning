(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var v0 Int)
(declare-var v1 Int)

(declare-rel fail ())

(rule (=> (and (> x0 y0) (> y0 z0) (= v0 0))
    (inv x0 y0 z0 v0)))

(rule (=> (and
        (inv x0 y0 z0 v0)
        (= x1 (+ x0 1))
        (= y1 (+ y0 3))
        (= z1 (+ z0 2))
        (= v1 (ite (< x0 y0) (+ v0 1) v0)))
    (inv x1 y1 z1 v1)))

(rule (=> (and (inv x0 y0 z0 v0) (> (- z0 x0) 72531)
    (not (> v0 0))) fail))

(query fail)
