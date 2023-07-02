(declare-rel inv (Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (and (= i 7610) (= j 1)) (inv i j)))

(rule (=> 
    (and 
        (inv i j)
        (= i1 (+ i 7610))
        (= j1 (+ j 1))
    )
    (inv i1 j1)
  )
)

(rule (=> (and (inv i j) (not (= (div i 7610) j))) fail))

(query fail :print-certificate true)