(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var w0 Int)
(declare-var w1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 z0) (= y0 0) (= w0 1)
        (or (= z0 0) (= z0 1)))
    (inv x0 y0 w0 z0)))

(rule (=> (and
        (inv x0 y0 w0 z0)
        (= x1 (+ 1 x0))
        (= y1 (+ y0 x0 (- 3)))
        (= z1 (- 1 z0))
        (= w1 (ite (= z0 (mod x0 2))
            (+ w0 y0) (- w0 1))))
    (inv x1 y1 w1 z1)))

(rule (=> (and (inv x0 y0 w0 z0) (> x0 10)
    (not (>= w0 0))) fail))

(query fail)

