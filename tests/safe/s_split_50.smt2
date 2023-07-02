(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 0) (= z0 0) (= w0 0))
    (inv x0 y0 z0 w0)))

(rule (=> (and
        (inv x0 y0 z0 w0)
        (= x1 (mod (+ x0 1) 2000))
        (= y1 (+ y0 1))
        (= z1 (ite (< x0 1000) (+ z0 1) z0))
        (= w1 (ite (>= x0 1000) (+ w0 1) w0)))
    (inv x1 y1 z1 w1)))

(rule (=> (and (inv x0 y0 z0 w0) (= y0 999000)
    (not (= 1000 (- z0 w0)))) fail))

(query fail)
