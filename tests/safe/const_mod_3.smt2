(declare-rel inv (Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (and (= i 0) (= j 0)) (inv i j)))

(rule (=> 
    (and 
        (inv i j)
        (= i1 (+ i 1))
        (= j1 (ite (= j 0) 1 0))
    )
    (inv i1 j1)
  )
)

(rule (=> (and (inv i j) (not (ite (= j 1) (= (mod i 2) 1) (= (mod i 2) 0)))) fail))

(query fail :print-certificate true)