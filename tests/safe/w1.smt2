(declare-rel itp (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (and (>= n 0) (= x 0)) (itp x n)))

(rule (=> 
    (and 
        (itp x n)
        (< x n)
        (= x1 (+ x 1))
    )
    (itp x1 n)
  )
)


(rule (=> (and (itp x n) (>= x n) (not (= x n))) fail))


(query fail :print-certificate true)

