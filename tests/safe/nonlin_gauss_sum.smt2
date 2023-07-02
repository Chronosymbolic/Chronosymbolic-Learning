(declare-rel inv (Int Int Int))
(declare-var i Int)
(declare-var n Int)
(declare-var sum Int)
(declare-var i1 Int)
(declare-var sum1 Int)

(declare-rel fail ())

(rule (=> (and (= sum 0) (= i 1) (<= 1 n) (<= n 1000)) (inv i n sum)))

(rule (=> 
    (and 
	(inv i n sum)
        (< i n)
        (= sum1 (+ sum i))
        (= i1 (+ i 1))
    )
    (inv i1 n sum1)
  )
)

(rule (=> (and (inv i n sum) (= i n) (not (= (+ (* 2 sum) (* 2 n)) (* n (+ n 1))))) fail))

(query fail :print-certificate true)