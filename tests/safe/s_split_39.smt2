(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= z0 0))
    (inv x0 z0)))

(rule (=> (and
        (inv x0 z0)
        (= x1 (ite (< (* x0 5) z0) (+ x0 1) (div x0 10)))
        (= z1 (ite (< (* x0 5) z0) z0 (+ 1 z0))))
    (inv x1 z1)))

(rule (=> (and (inv x0 z0) (> z0 50)
    (not (> z0 x0))) fail))

(query fail)
