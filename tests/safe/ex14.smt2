(declare-rel itp (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (and (= x 1)) (itp x y n)))

(rule (=> 
    (and 
        (itp x y n)
        (<= x n)
        (= y1 (- n x))
        (= x1 (+ x 1))
    )
    (itp x1 y1 n)
  )
)


(rule (=> (and (itp x y n) (<= x n) (= y1 (- n x)) (or (< y1 0) (>= y1 n))) fail))


(query fail :print-certificate true)

