(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (= x0 0) (inv x0 y0 z0)))

(rule (=> (and
        (inv x0 y0 z0)
        (= x1 (+ 1 x0))
        (= y1 (ite (>= x0 765552) (ite (>= x0 865552) y0 (+ y0 1)) 0))
        (= z1 (ite (>= x0 663258) (ite (>= x0 763258) z0 (+ z0 1)) 0)))
    (inv x1 y1 z1)))

(rule (=> (and (inv x0 y0 z0) (>= x0 965552)
    (not (= y0 z0))) fail))

(query fail)
