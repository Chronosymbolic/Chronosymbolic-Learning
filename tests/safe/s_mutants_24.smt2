(declare-rel itp (Int Int Int Int))
(declare-rel fail ())
(declare-var i1 Int)
(declare-var i1p Int)
(declare-var i2 Int)
(declare-var i2p Int)
(declare-var N1 Int)
(declare-var N2 Int)

(rule (=> (and (= N1 N2) (= i1 N1) (= i2 0)) (itp i1 i2  N1 N2)))

(rule (=> 
    (and
        (itp i1 i2 N1 N2)
        (> i1 0)
        (< i2 N1)
        (= i1p (- i1 1))
        (= i2p (+ i2 1))
    )
    (itp i1p i2p  N1 N2)
  )
)

;(rule (=> (and (itp i1 i2 N1 N2) (= i1 0) (not (= i2 N1))) fail))
;(rule (=> (and (itp i1 i2 N1 N2) (= i2 N1) (not (= i1 0))) fail))

(rule (=> (and (itp i1 i2 N1 N2) (not (= (= i2 N1) (= i1 0)))) fail))

(query fail :print-certificate true)

