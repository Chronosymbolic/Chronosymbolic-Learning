(declare-rel inv (Int))
(declare-var x0 Int)
(declare-var x1 Int)

(declare-rel fail ())

(rule (=> (= x0 0) (inv x0 )))

(rule (=> (and (inv x0) (= x1 (ite (= x0 9998) 1 (+ x0 2)))) (inv x1)))

(rule (=> (and (inv x0) (= 0 (mod x0 4)) (not (<= x0 9996))) fail))

(query fail)

