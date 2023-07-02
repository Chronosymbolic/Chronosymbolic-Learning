(declare-rel inv1 (Int Int Int))
(declare-rel inv2 (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var LRG1 Int) ; 65520
(declare-var LRG2 Int) ; 268435455
(declare-var tmp1 Int)
(declare-var tmp2 Int)

(declare-rel fail ())

(rule (=> (and 
        (= x0 0) (< 0 LRG1) (< LRG1 LRG2) 
        (= LRG1 (* 2 tmp1))
        (= LRG2 (+ (* 2 tmp2) 1)))
    (inv1 x0 LRG1 LRG2)))

(rule (=> 
    (and 
        (inv1 x0 LRG1 LRG2)
        (< x0 LRG1)
        (= x1 (ite (< x0 LRG1) (+ x0 1) (+ x0 2)))
    )
    (inv1 x1 LRG1 LRG2)
  )
)

(rule (=> (and (inv1 x0 LRG1 LRG2) (not (< x0 LRG1))) (inv2 x0 LRG1 LRG2)))

(rule (=>
    (and
        (inv2 x0 LRG1 LRG2)
        (< x0 LRG2)
        (= x1 (ite (< x0 LRG1) (+ x0 1) (+ x0 2)))
    )
    (inv2 x1 LRG1 LRG2)
  )
)

(rule (=> (and (inv2 x0 LRG1 LRG2) (>= x0 LRG2)
   (not (= (mod x0 2) 0))) fail))

(query fail)
