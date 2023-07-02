(declare-rel FUN (Int Int Int))
(declare-rel SAD (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= y 0) (= n 0)) (FUN x y n)))

(rule (=> 
    (and 
        (FUN x y n)
        (= x1 (+ x 1))
        (= y1 (+ y 1))
    )
    (FUN x1 y1 n)
  )
)

(rule (=> (FUN x y n) (SAD x y n)))

(rule (=> 
    (and 
        (SAD x y n)
        (or (<= x (- n 1)) (>= x (+ n 1)))
        (= x1 (- x 1))
        (= y1 (- y 1))
    )
    (SAD x1 y1 n)
  )
)

(rule (=> (and (SAD x y n) (= x n) (not (= y n))) fail))

(query fail :print-certificate true)

