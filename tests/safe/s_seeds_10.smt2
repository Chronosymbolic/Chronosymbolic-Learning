(declare-rel itp (Int))
(declare-var m Int)
(declare-var m1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var b Int)

(declare-rel fail ())

(rule (=> (and (= i 0)) (itp i)))

(rule (=> 
    (and 
        (itp i)
        (= i1 (- i))
    )
    (itp i1)
  )
)


(rule (=> (and (itp i) (not (= i 0))) fail))


(query fail :print-certificate true)
