(declare-rel inv (Int Int Int))
(declare-rel inv1 (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var n0 Int)
(declare-var n1 Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0) (> n0 0)) (inv x1 y1 n0)))

(rule (=> (and (inv x1 y1 n0) (= n1 (- n0 1))) (inv1 x1 y1 n1)))

(rule (=> 
    (and 
        (inv1 x0 y0 n0)
        (< x0 n0)
        (or (= y1 x0) (= y1 y0))
        (= x1 (+ x0 1))
    )
    (inv1 x1 y1 n0)
  )
)

(rule (=> (and (inv1 x1 y1 n0) (= n1 (+ n0 1))) (inv x1 y1 n1)))

(rule (=> (and (inv x1 y1 n0) (>= x1 n0) (not (and (<= 0 y1) (<= y1 n0)))) fail))

(query fail :print-certificate true)
