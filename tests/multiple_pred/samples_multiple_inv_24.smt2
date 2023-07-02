(declare-rel FUN (Int Int Int Int))
(declare-rel SAD (Int Int Int Int))
(declare-var k Int)
(declare-var k1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var f Int)
(declare-var f1 Int)
(declare-var N Int)
(declare-var N1 Int)

(declare-rel fail ())

(rule (=> (and (= k 0) (= j 0) (> N 0) (= N (+ (* 2 N1) 1))) (FUN k j 0 N)))

(rule (=> 
    (and 
        (FUN k j f N)
        (< k N)
        (= k1 (+ k 1))
        (= f1 (ite (= f 0) 1 0))
        (= j1 (ite (= f 0) (+ j 1) j))
    )
    (FUN k1 j1 f1 N)
  )
)

(rule (=> (and (FUN k j f N) (>= j N) (= k1 0) (= j1 j)) (SAD k1 j1 0 N)))

(rule (=>
    (and
        (SAD k j f N)
        (< k N)
        (= k1 (+ k 1))
        (= f1 (ite (= f 0) 1 0))
        (= j1 (ite (= f 1) (+ j 1) j))
    )
    (SAD k1 j1 f1 N)
  )
)

(rule (=> (and (SAD k j f N) (>= k N) (not (= N j))) fail))

(query fail)
