(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var v0 Int)
(declare-var v1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (=> (and (> x0 z0) (= v0 0) (= w0 0))
    (inv x0 z0 v0 w0)))

(rule (=> (and
        (inv x0 z0 v0 w0)
        (= x1 (+ x0 1))
        (= z1 (+ z0 2))
        (= v1 (ite (< x0 z0) (+ v0 1) v0))
        (= w1 (ite (< x0 z0) w0 (+ w0 1))))
    (inv x1 z1 v1 w1)))

(rule (=> (and (inv x0 z0 v0 w0) (> v0 1000)
    (not (> w0 0))) fail))

(query fail)
