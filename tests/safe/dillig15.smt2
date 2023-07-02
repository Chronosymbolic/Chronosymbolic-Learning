(declare-rel itp (Int Int Int))
(declare-var j Int)
(declare-var k Int)
(declare-var n Int)
(declare-var j1 Int)
(declare-var k1 Int)
(declare-var n1 Int)

(declare-rel fail ())

(rule (=> (and (>= n 1) (> k n) (= j 0)) (itp j k n)))

(rule (=> 
    (and 
	(itp j k n)
        (<= j (- n 1))
	(= j1 (+ j 1))
	(= k1 (- k 1))
    )
    (itp j1 k1 n)
  )
)


(rule (=> (and (itp j k n) (>= j n) (<= k -1)) fail))

(query fail :print-certificate true)

