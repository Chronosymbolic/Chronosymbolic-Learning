(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0) (>= n 0)) (inv x1 y1 n)))

(rule (=> 
    (and 
        (inv x0 y0 n)
        (< x0 n)
        (= x1 (+ x0 1))
        (= y1 (+ y0 x1))
    )
    (inv x1 y1 n)
  )
)

(rule (=> (and (inv x1 y1 n) (>= x1 n) (not (> (+ 1 x1 y1) (* 2 n)))) fail))

(query fail :print-certificate true)