(declare-rel WRAP (Int Int Int Int))
(declare-rel NEST (Int Int Int Int))
(declare-rel WEEE (Int Int Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var k Int)
(declare-var k1 Int)
(declare-var n Int)

(declare-rel fail ())

(rule (=> (= i 0) (WRAP i j k n)))

(rule (=> (and (WRAP i j k n) (< i n) (= j i)) (NEST i j k n)))

(rule (=> (and (NEST i j k n) (= k j) (< j n)) (WEEE i j k n)))

(rule (=> 
    (and 
        (WEEE i j k n)
        (< k n)
        (= k1 (+ k 1))
    )
    (WEEE i j k1 n)
  )
)

(rule (=> (and (WEEE i j k n) (= j1 (+ j 1)) (= k n)) (NEST i j1 k n)))

(rule (=> (and (NEST i j k n) (= i1 (+ i 1)) (= j n)) (WRAP i1 j k n)))

(rule (=> (and (WEEE i j k n) (<= k (- i 1))) fail))

(query fail :print-certificate true)

