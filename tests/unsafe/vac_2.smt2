(declare-rel a (Int))
(declare-rel b (Int))
(declare-rel c (Int))
(declare-rel v (Int))
(declare-rel d (Int))
(declare-rel e (Int))
(declare-rel f (Int))
(declare-rel fail ())

(declare-var x Int)

(rule (=> (a x) (b x)))
(rule (=> (b x) (c x)))
(rule (=> (c x) (v x)))
(rule (=> (v x) (d x)))
(rule (e 0))
(rule (=> (e x) (d x)))
;(rule (=> (d x) (ite (= x 5) (f x) (d (+ x 1))))) ; should be automatically reritten
(rule (=> (and (d x) (= x 5)) (f x)))
(rule (=> (and (d x) (not (= x 5))) (d (+ x 1))))
(rule (=> (and (f x) (not (= x 6))) fail))

(query fail)
