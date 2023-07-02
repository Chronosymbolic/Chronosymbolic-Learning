(declare-rel I (Int))
(declare-rel J (Int Int))
(declare-rel K (Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var z Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (= x 0) (I x)))

(rule (=> (and (I x) (= x1 x) (= y1 0)) (J x1 y1)))

(rule (=> (and (J x y) (= x1 x) (= y1 (+ y 1))) (J x1 y1)))

(rule (=> (and (J x y) (= x1 (+ x y))) (I x1)))

(rule (=> (and (I x) (= z1 (- x))) (K z1)))

(rule (=> (and (K z) (= z1 (- z 1))) (K z1)))

(rule (=> (and (K z) (not (<= z 0))) fail))

(query fail)
