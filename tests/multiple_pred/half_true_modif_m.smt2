(declare-rel inv1 (Int Int Int Int))
(declare-rel inv (Int Int Int Int))
(declare-var i Int)
(declare-var k Int)
(declare-var k1 Int)
(declare-var n Int)
(declare-var i1 Int)
(declare-var n1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (and (= i 0) (= j 0) (= n 0) (>= k 0)) (inv1 i k n j)))

(rule (=> (and (inv1 i k n j) (= k1 (+ k 1))) (inv1 i k1 n j)))

(rule (=> (and (inv1 i k n j) (= k1 (+ k 52))) (inv i k1 n j)))

(rule (=> 
    (and 
        (inv i k n j)
        (< i (* 2 k))
        (= n1 (ite (= j 0) (+ n 1) n))
        (= i1 (+ i 1))
        (= j1 (ite (= j 0) 1 0))
    )
    (inv i1 k n1 j1)
  )
)

(rule (=> (and (inv i k n j) (>= i (* 2 k)) (not (= n k))) fail))

(query fail :print-certificate true)
