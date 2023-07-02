(declare-rel inv (Int Int Int))
(declare-var i Int)
(declare-var k Int)
(declare-var n Int)
(declare-var i1 Int)
(declare-var n1 Int)

(declare-rel fail ())

(rule (=> (and (= i 0) (= n 0) (>= k 0)) (inv i k n)))

(rule (=> 
    (and 
	(inv i k n)
	(< i (* 2 k))
        (= n1 (ite (= (mod i 2) 0) (+ n 1) n))
        (= i1 (+ i 1))
    )
    (inv i1 k n1)
  )
)

(rule (=> (and (inv i k n) (>= i (* 2 k)) (not (= n k))) fail))

(query fail :print-certificate true)