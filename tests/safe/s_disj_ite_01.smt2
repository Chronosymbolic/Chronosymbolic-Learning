(declare-rel itp (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x3 Int)
(declare-var x4 Int)
(declare-var x5 Int)
(declare-var x6 Int)
(declare-var x7 Int)
(declare-var x8 Int)
(declare-var x9 Int)

(declare-rel fail ())


(rule (=>
    (and (= x1 0) (= x3 100)) (itp x1 x3)
  )
)

(rule (=> 
    (and 
	(itp x1 x3)
        (= x2 (+ x1 1))
        (= x4 (+ (ite (> x2 0) 1 0)
                 (ite (> x3 10) -1 x3)))

    )
    (itp x2 x4)
  )
)


(rule (=> (and (itp x1 x3) (> x1 10)
   (not 
     (< x3 x1)
   )) fail))


(query fail :print-certificate true)

