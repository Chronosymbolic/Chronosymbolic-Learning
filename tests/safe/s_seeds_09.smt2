(declare-rel itp (Int Int))
(declare-var m Int)
(declare-var m1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var b Int)

(declare-rel fail ())


(rule (=> (and (= m 2) (= i 1)) (itp m i)))

(rule (=> 
    (and 
        (itp m i)
        (> m i)
        (= m1 (+ m 1))
        (= i1 (+ i 1))
    )
    (itp m1 i1)
  )
)


(rule (=> (and (itp m i) (> i 80) (not (> m 81))) fail))

(query fail :print-certificate true)