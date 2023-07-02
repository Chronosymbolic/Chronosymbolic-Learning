(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 1) (= z0 0))
    (inv x0 z0)))

(rule (=> (and
        (inv x0 z0)
        (= x1 (- x0))
        (= z1 (ite (= (mod x0 3) 1) (+ z0 x0) (- z0 x0))))
    (inv x1 z1)))

(rule (=> (and (inv x0 z0) (not (>= z0 0))) fail))

(query fail)
