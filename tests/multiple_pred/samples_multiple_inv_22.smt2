(declare-rel FUN (Int Int))
(declare-rel SAD (Int Int))
(declare-var k Int)
(declare-var k1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (and (= k 0) (= j 0)) (FUN k j)))

(rule (=> 
    (and 
      (FUN k j)
      (= k1 (+ k 1))
      (= j1 (+ j k1))
    )
    (FUN k1 j1)
  )
)

(rule (=> (and (FUN k j) (> k 0) (= k1 k) (= j1 (+ j 1))) (SAD k1 j1)))

(rule (=>
    (and
        (SAD k j)
        (> j 0)
        (= k1 (- k 1))
        (= j1 (- j k1))
    )
    (SAD k1 j1)
  )
)

(rule (=> (and (SAD k j) (<= j 0) (not (< k 0))) fail))

(query fail)

