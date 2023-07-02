(declare-rel itp (Int Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var m Int)
(declare-var n Int)
(declare-var x1 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= y m) (>= n 0) (>= m 0) (< m (- n 1))) (itp x y m n)))

(rule (=> 
    (and 
	(itp x y m n)
        (<= x (- n 1))
        (= x1 (+ x 1))
	(= y1 (ite (>= x1(+ m 1)) (+ y 1) y))
        (or (>= x1 (+ m 1)) (<= x1 m))
    )
    (itp x1 y m n)
  )
)


(rule (=> (and (itp x y m n) (> x (- n 1)) (>= y (+ n 1))) fail))

(query fail :print-certificate true)

