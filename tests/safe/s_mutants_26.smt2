(declare-rel inv (Int Int Int Int))
(declare-var k0 Int)
(declare-var k1 Int)
(declare-var i0 Int)
(declare-var i1 Int)
(declare-var j0 Int)
(declare-var j1 Int)
(declare-var n0 Int)
(declare-var n1 Int)
(declare-var b0 Int)
(declare-var b1 Int)

(declare-rel fail ())

(rule (=> (and (= i1 j1) (>= j1 0) (= n1 0) (= k1 0))
          (inv k1 i1 j1 n1)))

(rule (=> 
    (and 
        (inv k0 i0 j0 n0)
        (= i1 (+ i0 1))
        (= j1 (- j0 1))
        (= k1 (ite (>= i0 j0) (+ k0 i0) k0))
        (= n1 (ite (>= i0 j0) n0 (+ n0 j0)))
    )
    (inv k1 i1 j1 n1)
  )
)

(rule (=> (and (inv k1 i1 j1 n1) (not (>= k1 n1))) fail))

(query fail :print-certificate true)
