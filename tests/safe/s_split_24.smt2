(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (or (= x0 0) (= x0 1))
               (or (= y0 0) (= y0 1)) (= z0 0))
    (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ x0 2))
        (= y1 (+ y0 3))
        (= z1 (ite (= (mod x0 2) (mod y0 2)) (+ 1 z0) z0)))
    (inv x1 y1 z1)))

(rule (=> (and (inv x0 y0 z0) (> x0 400)
    (not (>= z0 100))) fail))

(query fail)
