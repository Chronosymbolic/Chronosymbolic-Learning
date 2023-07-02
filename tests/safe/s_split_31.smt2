(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var w0 Int)
(declare-var w1 Int)
(declare-var z0 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (> z0 36239) (= w0 0))
    (inv x0 z0 w0)))

(rule (=> (and
        (inv x0 z0 w0)
        (= x1 (+ 1 x0))
        (= w1 (ite (or (< x0 z0) (= 0 (mod x0 2)))
            (+ w0 1) (- w0 1))))
    (inv x1 z0 w1)))

(rule (=> (and (inv x0 z0 w0) (> x0 z0)
    (not (>= w0 0))) fail))

(query fail)

