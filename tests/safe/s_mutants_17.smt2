(declare-rel itp (Int Int Int))
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x3 Int)
(declare-var x4 Int)
(declare-var y Int)

(declare-rel fail ())

(rule (=> (and 

  (= x1 0) (> y 0) (< y 5) (= x3 (* 3 y))
; (= x1 0) (>= x3 3) (<= x3 12)

) (itp x1 x3 y )))

(rule (=> 
    (and 
        (itp x1 x3 y )
        (< x1 1000)
        (= x2 (+ x1 1))
        (= x4 (+ x3 1))
    )
    (itp x2 x4 y)
  )
)

(rule (=> (and (itp x1 x3 y)
   (not (and (>= x3 3) (<= x3 1012))
)) fail))

(query fail :print-certificate true)