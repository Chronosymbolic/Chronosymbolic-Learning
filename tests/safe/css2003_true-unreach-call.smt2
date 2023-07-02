(declare-rel inv (Int Int Int Int Int))
(declare-var i0 Int)
(declare-var i1 Int)
(declare-var j0 Int)
(declare-var j1 Int)
(declare-var k0 Int)
(declare-var k1 Int)
(declare-var LRG1 Int) ; 1000
(declare-var LRG2 Int) ; 268435455

(declare-rel fail ())

(rule (=> (and (= i1 1) (= j1 1) (<= 0 k1) (<= k1 1)
        (< LRG1 LRG2) 
        (= LRG1 1000))
    (inv i1 j1 k1 LRG1 LRG2)))

(rule (=> 
    (and 
        (inv i0 j0 k0 LRG1 LRG2)
        (< i0 LRG2)
        (= i1 (+ i0 1))
        (= j1 (+ j0 k0))
        (= k1 (- k0 1))
    )
    (inv i1 j1 k1 LRG1 LRG2)
  )
)

(rule (=> (and (inv i0 j0 k0 LRG1 LRG2) (< i0 LRG2)
   (not (and (<= 1 (+ i0 k0)) (<= (+ i0 k0) 2) (>= i0 1)))) fail))

(query fail :print-certificate true)