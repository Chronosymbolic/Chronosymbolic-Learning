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

(rule (=> (and (= x0 52) (= y0 97) (= z0 (- 76)) (= w0 0))
    (inv x0 y0 z0 w0)))

(rule (=> (and
        (inv x0 y0 z0 w0)
        (= x1 (- 13 (* 7 x0)))
        (= y1 (- 54 (* 2 y0)))
        (= z1 (+ (* (- 5) x0) (* 3 y0) (* 4 z0) (- 8754)))
        (= w1 (ite (> z1 0) (- w0 x0) w0)))
    (inv x1 y1 z1 w1)))

(rule (=> (and (inv x0 y0 z0 w0) (>= y0 80914)
    (not (> w0 0))) fail))

(query fail)

