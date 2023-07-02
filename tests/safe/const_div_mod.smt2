(declare-rel inv (Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (= i j) (inv i j)))

(rule (=> 
    (and 
        (inv i j)
        (> i 0)
        (= (mod i 2) 0)
        (= i1 (div i 2))
    )
    (inv i1 j)
  )
)

(rule (=> (and (inv i j) (= i 0) (not (= (mod j 2) 0))) fail))

(query fail :print-certificate true)