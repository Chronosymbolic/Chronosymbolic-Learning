(declare-rel WRAP (Int Int Int Int))
(declare-rel NEST (Int Int Int Int))
(declare-var i Int)
(declare-var j Int)
(declare-var i1 Int)
(declare-var j1 Int)
(declare-var x Int)
(declare-var y Int)
(declare-var x1 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= y 0) (= i 0) (= j 0)) (WRAP x y i j)))

(rule (=> (WRAP x y i j) (NEST x y i j)))

(rule (=> 
    (and 
      (NEST x y i j)
      (= i1 (ite (= x y) (+ i 1) i))
      (= j1 (ite (= x y) j (+ j 1)))
    )
    (NEST x y i1 j1)
  )
)

(rule (=>
    (and 
        (NEST x y i j)
        (= y1 (+ y 1))
        (= x1 (ite (>= i j) (+ x 1) x))
    )
    (WRAP x1 y1 i j)
  )
)

(rule (=> (and (WRAP x y i j) (<= i (- j 1))) fail))

(query fail :print-certificate true)

