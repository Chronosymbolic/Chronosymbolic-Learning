(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var n Int)
(declare-var flag Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0) (= n (ite (= flag 1) 1 2))) (inv x1 y1 n flag)))

(rule (=> 
    (and 
        (inv x0 y0 n flag)
        (= x1 (+ x0 1))
        (= y1 (+ y0 n))
    )
    (inv x1 y1 n flag)
  )
)

(rule (=> (and (inv x1 y1 n flag) (= flag 1) (not (= x1 y1))) fail))

(query fail :print-certificate true)