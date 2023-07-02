(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= z0 0))
    (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ 1 x0))
        (= z1 (ite (= y0 (div x0 1000)) (+ z0 1) z0)))
    (inv x1 y0 z1)))

(rule (=> (and (inv x0 y0 z0) (> x0 (* 1000 (+ 1 y0))) (>= y0 0)
    (not (= z0 1000))) fail))

(query fail)
