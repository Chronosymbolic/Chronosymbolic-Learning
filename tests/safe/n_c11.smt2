(declare-rel inv (Int))
(declare-var len0 Int)
(declare-var len1 Int)
(declare-var len2 Int)

(declare-rel fail ())

(rule (=> (= len0 0) (inv len0)))

(rule (=> 
    (and 
        (inv len0)
        (= len1 (ite (= len0 4) 0 len0))
        (= len2 (+ len1 1))
    )
    (inv len2)
  )
)


(rule (=> (and (inv len0) 
   (not (and (>= len0 0) (<= len0 5)))) fail))


(query fail :print-certificate true)

