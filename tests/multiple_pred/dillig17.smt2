(declare-rel WRAP (Int Int Int Int))
(declare-rel NEST (Int Int Int Int))
(declare-var i Int)
(declare-var j Int)
(declare-var k Int)
(declare-var n Int)
(declare-var i1 Int)
(declare-var j1 Int)
(declare-var k1 Int)
(declare-var n1 Int)

(declare-rel fail ())

(rule (=> (and (= k 1) (= i 1) (= j 0)) (WRAP i j k n)))

(rule (=> (and (WRAP i j k n) (<= i (- n 1)) (= j1 0)) (NEST i j1 k n)))

(rule (=> 
    (and 
        (NEST i j k n)
        (<= j (- i 1))
        (= k1 (+ k (- i j)))
        (= j1 (+ j 1))
    )
    (NEST i j1 k1 n)
  )
)

(rule (=> (and (NEST i j k n) (>= j i) (= i1 (+ i 1))) (WRAP i1 j k n)))

(rule (=> (and (WRAP i j k n) (> i (- n 1)) (>= i n) (<= k (- n 1))) fail))

(query fail :print-certificate true)

