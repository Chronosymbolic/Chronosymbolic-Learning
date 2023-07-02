(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 -100) (= z0 -100))
    (inv x0 z0)))

(rule (=> (and
        (inv x0 z0)
        (= x1 (mod (+ x0 1) 5))
        (= z1 (ite (< z0 4) (+ z0 1) (mod z0 4))))
    (inv x1 z1)))

(rule (=> (and (inv x0 z0) (>= z0 0)
    (not (= x0 z0))) fail))

(query fail)
