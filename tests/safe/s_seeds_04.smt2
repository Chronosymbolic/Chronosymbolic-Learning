(declare-rel itp (Int Int))
(declare-var m Int)
(declare-var m1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var b Int)

(declare-rel fail ())

(rule (=> (and (= m 0) (= i 0)) (itp m i)))

(rule (=> 
    (and 
        (itp m i)
        (= i1 (- i))
        (= m1 (+ m 1))
    )
    (itp m1 i1)
  )
)


(rule (=> (and (itp m i) (= m 1000) (not (>= i 0))) fail))


(query fail :print-certificate true)
