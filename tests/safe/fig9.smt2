(declare-rel itp (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= y 0)) (itp x y)))

(rule (=> 
    (and 
        (itp x y)
        (>= y 0)
        (= y1 (+ y x))
    )
    (itp x y1)
  )
)


(rule (=> (and (itp x y) (< y 0)) fail))


(query fail :print-certificate true)

