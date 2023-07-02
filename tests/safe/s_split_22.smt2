(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 767976) (= z0 0))
    (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ x0 1))
        (= y1 (- y0 1))
        (= z1 (ite (= (mod (- x0 y0) 3) 1) (+ 3 z0) z0)))
    (inv x1 y1 z1)))

(rule (=> (and (inv x0 y0 z0) (>= x0 280275)
    (not (>= z0 280275))) fail))

(query fail)

