(declare-rel inv (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var n Int)
(declare-var n1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= n 0)) (inv x n)))

(rule (=> 
    (and 
        (inv x n)
        (= n1 (+ n 1))
        (= x1 (+ x (* 2 n1) -1))
    )
    (inv x1 n1)
  )
)


(rule (=> (and (inv x n) (not (= x (* n n)))) fail))


(query fail :print-certificate true)

