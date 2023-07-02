(declare-rel FUN (Int Int Int Int))
(declare-rel SAD (Int Int Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var k Int)
(declare-var k1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (and (= i 0) (= k 0)) (FUN i j k n)))

(rule (=> 
    (and 
        (FUN i j k n)
        (< i n)
        (= i1 (+ i 1))
        (= k1 (+ k 1))
    )
    (FUN i1 j k1 n)
  )
)

(rule (=> (and (FUN i j k n) (= i n) (= j1 n)) (SAD i j1 k n)))

(rule (=> 
    (and 
        (SAD i j k n)
        (> j 0)
        (= k1 (- k 1))
        (= j1 (- j 1))
    )
    (SAD i j1 k1 n)
  )
)

(rule (=> (and (SAD i j k n) (> j 0) (not (> k 0))) fail))

(query fail :print-certificate true)

