(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 0))
    (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (+ 1 x0))
        (= y1 (ite (>= x0 5000)
          (ite (>= x0 10000) y0 (+ y0 1)) 0)))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (>= x0 10000)
    (not (= y0 5000))) fail))

(query fail)
