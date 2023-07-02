(declare-rel inv (Int Int Int Int Int))
(declare-rel inv1 (Int Int ))
(declare-var c1 Int)
(declare-var c2 Int)
(declare-var c3 Int)
(declare-var c4 Int)
(declare-var k0 Int)
(declare-var k1 Int)
(declare-var i0 Int)
(declare-var i1 Int)
(declare-var n0 Int)
(declare-var n1 Int)
(declare-var x1 Int)
(declare-var v0 Int)
(declare-var v1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (inv1 10 20))

(rule (=> (and (inv1 c1 c2) (= c3 (+ c1 c1)) (= c4 (+ c2 c2))) (inv1 c3 c4)))

(rule (=> (and (inv1 c1 c2)  (= k1 0) (= i1 0) (> n1 0) (< n1 10))
          (inv c1 c2 k1 i1 n1)))

(rule (=> 
    (and 
        (inv c1 c2 k0 i0 n0)
        (< i0 n0)
        (= i1 (+ i0 1))
        (= w1 (mod w0 2))
        (= v1 (ite (= w1 0) 0 1))
        (= k1 (ite (= v1 0) (+ k0 c1) (+ k0 c2)))
    )
    (inv c1 c2 k1 i1 n0)
  )
)

(rule (=> (and (inv c1 c2 k1 i1 n1) (>= i1 n1) (not (> k1 n1))) fail))

(query fail :print-certificate true)
