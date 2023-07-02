(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 1000) (= z0 100))
    (inv x0 z0)))

(rule (=> (and
        (inv x0 z0)
        (= x1 (ite (< (div x0 10) z0) (+ x0 1) (- x0 1)))
        (= z1 (ite (< (div x0 10) z0) (- z0 1) (+ z0 1))))
    (inv x1 z1)))

(rule (=> (and (inv x0 z0) (not (< z0 x0))) fail))

(query fail)
