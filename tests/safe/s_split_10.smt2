(declare-rel inv (Int))
(declare-var x0 Int)
(declare-var x1 Int)

(declare-rel fail ())

(rule (=> (= x0 0) (inv x0 )))

(rule (=> (and (inv x0) (= x1 (ite (< (div x0 5) 200) (+ x0 1) (+ x0 5)))) (inv x1)))

(rule (=> (and (inv x0) (>= x0 2000) (not (= (mod x0 5) 0))) fail))

(query fail)

