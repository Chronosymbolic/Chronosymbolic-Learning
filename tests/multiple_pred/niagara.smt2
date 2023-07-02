(declare-rel itp1 (Int Int))
(declare-rel itp2 (Int Int))
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x4 Int)
(declare-var y1 Int)
(declare-var y2 Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0)) (itp1 x1 y1)))

(rule (=> 
    (and 
        (itp1 x1 y1)
        (< y1 100000)
        (= x2 (+ x1 1))
        (= y2 (+ y1 x2))
    )
    (itp1 x2 y2)
  )
)

(rule (=> (and (itp1 x1 y1) 
               (= y1 100000)
               (= x2 (+ x1 2))
               (= y2 (+ y1 x2))) 
          (itp2 x2 y2)))


(rule (=> (and (itp1 x1 y1) (< y1 100000) (> x1 y1)) fail))

(rule (=> 
    (and 
        (itp2 x1 y1)
        (> y1 100000)
        (= x2 (+ x1 1))
        (= y2 (+ y1 x2))

    )
    (itp2 x2 y2)
  )
)

(rule (=> (and (itp2 x1 y1) (> x1 y1)) fail))


(query fail :print-certificate true)
