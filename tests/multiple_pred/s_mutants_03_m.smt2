(declare-rel itp1 (Int Int Int  ))
(declare-rel itp2 (Int Int Int  ))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x3 Int)
(declare-var x4 Int)
(declare-var x5 Int)
(declare-var x6 Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= x3 0) (= x5 0)) (itp1 x1 x3 x5)))

(rule (=> 
    (and 
	      (itp1 x1 x3 x5)
        (= x2 (+ x1 1))
        (= x4 (+ x3 1))
	      (or (= x6 (+ x5 x2))
            (= x6 (+ x5 x4)))
    )
    (itp1 x2 x4 x6)
  )
)

(rule (=> (itp1 x1 x3 x5) (itp2 x1 x5 x3)))

(rule (=>
    (and
        (itp2 x1 x3 x5)
        (or (and (= x2 (+ x1 1)) (= x4 x3))
            (and (= x2 x1) (= x4 (+ x3 1))))
        (= x6 (+ x5 x2 x4))
    )
    (itp2 x2 x4 x6)
  )
)

(rule (=> (and (itp2 x1 x3 x5)
   (not 
     (>= x5 0)
   )) fail))

(query fail)
