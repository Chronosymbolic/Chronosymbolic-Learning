(declare-rel inv1 (Int Int))
(declare-rel itp1 (Int Int Int))
(declare-var j Int)
(declare-var k Int)
(declare-var n Int)
(declare-var j1 Int)
(declare-var k1 Int)
(declare-var n1 Int)

(declare-rel fail ())

(rule (=> (>= n 1) (inv1 n k)))

(rule (=> (and (inv1 n k) (not (> k n)) (= k1 (+ k 215))) (inv1 n k1 )))

(rule (=> (and (inv1 n k) (> k n) (= j 0)) (itp1 j k n)))

(rule (=> 
    (and 
	      (itp1 j k n)
        (<= j (- n 1))
        (= j1 (+ j 1))
        (= k1 (- k 1))
    )
    (itp1 j1 k1 n)
  )
)

(rule (=> (and (itp1 j k n) (>= j n) (<= k -1)) fail))

(query fail :print-certificate true)

