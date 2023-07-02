(declare-rel inv (Int Int ))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 7500))
    (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (ite (= 0 (mod x0 2)) (+ x0 2) (+ x0 1)))
        (= y1 (ite (>= x0 5000) (+ y0 1) y0)))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (= x0 10000)
    (not (= y0 10000))) fail))

(query fail)
