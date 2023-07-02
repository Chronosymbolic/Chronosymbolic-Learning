(declare-rel inv (Int))
(declare-var i Int)
(declare-var i1 Int)

(declare-rel fail ())

(rule (=> (= i 0) (inv i)))

(rule (=> 
    (and 
        (inv i)
        (= i1 (+ i 2))
    )
    (inv i1)
  )
)

(rule (=> (and (inv i) (not (= (mod i 2) 0))) fail))

(query fail :print-certificate true)