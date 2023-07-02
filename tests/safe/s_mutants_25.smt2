(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 0)) (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (+ x0 1))
        (= y1 (ite (>= y0 x0) 0 (+ y0 2))))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (= x0 y0)
    (not (= 0 (mod x0 2)))) fail))

(query fail :print-certificate true)

