(declare-rel PRE (Int Int Int Int Int))
(declare-rel POST1 (Int Int Int Int))
(declare-rel POST2 (Int Int Int Int))
(declare-rel POST3 (Int Int Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var k Int)
(declare-var k1 Int)
(declare-var n Int)
(declare-var n1 Int)
(declare-var m Int)
(declare-var m1 Int)

; same as samples_multiple_inv_13.smt2, but with one iterator more

(declare-rel fail ())

(rule (=> (>= n 0) (PRE n n 0 0 0)))

(rule (=> (and (PRE n m i j k) (not (= n 0))
    (= n1 (- n 1))
    (or
        (and (= i1 (+ i 1)) (= j1 j) (= k1 k))
        (and (= i1 i) (= j1 (+ j 1)) (= k1 k))
        (and (= i1 i) (= j1 j) (= k1 (+ k 1)))))
  (PRE n1 m i1 j1 k1)))

(rule (=> (and (PRE n m i j k) (= n 0)) (POST1 m i j k)))

(rule (=> (and (POST1 m i j k) (not (= i 0)) (= i1 (- i 1)) (= m1 (- m 1)) ) (POST1 m1 i1 j k)))

(rule (=> (and (POST1 m i j k) (= i 0)) (POST2 m i j k)))

(rule (=> (and (POST2 m i j k) (not (= j 0)) (= j1 (- j 1)) (= m1 (- m 1)) ) (POST2 m1 i j1 k)))

(rule (=> (and (POST2 m i j k) (= j 0)) (POST3 m i j k)))

(rule (=> (and (POST3 m i j k) (not (= k 0)) (= k1 (- j 1)) (= m1 (- m 1)) ) (POST3 m1 i j k1)))

(rule (=> (and (POST3 m i j k) (= k 0) (not (= m 0))) fail))

(query fail)
