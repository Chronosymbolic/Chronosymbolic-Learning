(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (inv 0 0 0))

(rule (=> (and (inv x0 y0 z0)
  (= x1 (+ x0 1))
  (= y1 (ite (= x0 0) 523 (+ y0 z0)))
  (= z1 (ite (= x0 0) z0 250))) (inv x1 y1 z1)))

(rule (=> (and (inv x0 y0 z0) (>= x0 10) (not (> y0 2500))) fail))

(query fail)
