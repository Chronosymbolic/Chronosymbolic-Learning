(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var c0 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 c0) (= c0 5000))
    (inv x0 y0 c0)))

(rule (=> (and
        (inv x0 y0 c0)
        (= x1 (+ x0 1))
        (= y1 (ite (>= x0 c0) (+ y0 1) (- y0 1))))
    (inv x1 y1 c0)))

(rule (=> (and (inv x0 y0 c0) (= x0 (* 2 c0))
    (not (= y0 c0))) fail))

(query fail)
