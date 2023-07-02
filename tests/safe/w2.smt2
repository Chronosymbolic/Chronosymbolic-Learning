(declare-rel itp (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var n Int)
(declare-var m Int)

(declare-rel fail ())

(rule (=> (and (>= n 0) (= x 0)) (itp x m n)))

(rule (=> 
    (and 
        (itp x m n)
        (< x n)
        (= x1 (ite (= m 1) (+ x 1) x))
    )
    (itp x1 m n)
  )
)


(rule (=> (and (itp x m n) (>= x n) (not (= x n))) fail))


(query fail :print-certificate true)

