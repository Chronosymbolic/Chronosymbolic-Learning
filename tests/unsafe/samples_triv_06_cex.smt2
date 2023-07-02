(declare-rel inv (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (inv 0 1))

(rule (=> (inv 0 y) (inv y 0)))

(rule (=> (and (inv x y) (not (= 1 y))) fail))

(query fail :print-certificate true)