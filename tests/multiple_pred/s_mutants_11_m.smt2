(declare-rel itp1 (Int Int Int))
(declare-rel itp2 (Int Int Int))
(declare-rel itp3 (Int Int Int))
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x3 Int)
(declare-var x4 Int)
(declare-var x5 Int)
(declare-var x6 Int)

(declare-rel fail ())

(rule (=> (and (= x1 1) (= x3 1) (= x5 1)) (itp1 x1 x3 x5)))

(rule (=> 
    (and 
        (itp1 x1 x3 x5)
        (= x2 (+ x1 1))
        (= x4 (+ x1 x1))
        (= x6 (+ x1 x1 x1))
    )
    (itp1 x2 x4 x6)
  )
)

(rule (=> (itp1 x1 x3 x5) (itp2 x1 x3 x5)))

(rule (=>
    (and
        (itp2 x1 x3 x5)
        (= x2 (+ x1 x1 1))
        (= x4 (+ x1 x1 x1))
        (= x6 (+ x1 x1 x1 x1 ))
    )
    (itp2 x2 x4 x6)
  )
)

(rule (=> (itp2 x1 x3 x5) (itp3 x1 x3 x5)))

(rule (=>
    (and
        (itp3 x1 x3 x5)
        (= x2 (+ x1 x1 x1 1))
        (= x4 (+ x1 x1 x1 x1))
        (= x6 (+ x1 x1 x1 x1 x1))
    )
    (itp3 x2 x4 x6)
  )
)


(rule (=> (and (itp3 x1 x3 x5)
   (not 
     (or 
       (> (- x5 x3) 300)
       (< x1 1000)
     )
   )) fail))


(query fail)

