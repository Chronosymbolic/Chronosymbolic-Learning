(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 0) (= z0 0))
    (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ 1 x0))
        (= y1 (mod (+ y0 1) 100))
        (= z1 (ite (= (div z0 100) (div x1 100)) z0 (+ z0 100))))
    (inv x1 y1 z1)))

(rule (=> (and (inv x0 y0 z0) (not (= x0 (+ z0 y0)))) fail))

(query fail)

