(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (= x0 0) (inv x0 y0)))

(rule (=> (and (inv x0 y0)
    (= x1 (ite (< (div x0 5) 200) (+ x0 1) (+ x0 5)))
    (= y1 (ite (= x0 1000) 0 y0)))
  (inv x1 y1)))

(rule (=> (and (inv x0 y0) (>= x0 2000) (not (= y0 0))) fail))

(query fail)

