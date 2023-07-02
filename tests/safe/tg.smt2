(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var y2 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var z2 Int)

(declare-rel fail ())

(rule (=> (= x0 0) (inv x0 y0 z0)))

(rule (=> (and (inv x0 y0 z0)
    (ite (>= x0 5)             (and (= x1 x0)        (= y1 (+ y0 1))  (= z1 z0))
                               (and (= x1 (+ x0 1))  (= y1 y0)        (= z1 z0)))
    (ite (<= y1 5)             (and (= x2 x1)        (= y2 y1)        (= z2 (+ z1 1)))
             (ite (> x1 y1)    (and (= x2 x1)        (= y2 (+ y1 1))  (= z2 z1))
                               (and (= x2  0)        (= y2 y1)        (= z2 z1)))))
    (inv x2 y2 z2)))

(rule (=> (and (inv x0 y0 z0)
    (ite (>= x0 5)             (and (= x1 x0)       (= y1 (+ y0 1))  (= z1 z0))
                               (and (= x1 (+ x0 1)) (= y1 y0)        (= z1 z0)))
    (> y1 5) (> x1 y1)) fail))

(query fail)
