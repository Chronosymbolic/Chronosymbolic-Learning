(declare-rel inv (Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (and (= i 2) (= j 1)) (inv i j)))

(rule (=> 
    (and 
        (inv i j)
        (= i1 (+ i 2))
        (= j1 (+ j 1))
    )
    (inv i1 j1)
  )
)

(rule (=> (and (inv i j) (not (= (div i 2) j))) fail))

(query fail :print-certificate true)