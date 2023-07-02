(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)

(declare-rel fail ())

(rule (=> (and (< x0 0) (> y0 x0) (or (= z0 0) (= z0 1)))
    (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ x0 1))
        (= y1 (ite (= (mod x0 2) z0) (+ y0 2) y0)))
    (inv x1 y1 z0)))

(rule (=> (and (inv x0 y0 z0) (> x0 54932)
    (not (> y0 54932))) fail))

(query fail)
