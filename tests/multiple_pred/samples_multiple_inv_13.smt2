(declare-rel PRE (Int Int Int Int ))
(declare-rel POST1 (Int Int Int ))
(declare-rel POST2 (Int Int Int ))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var n Int)
(declare-var n1 Int)
(declare-var m Int)
(declare-var m1 Int)

(declare-rel fail ())

(rule (=> (>= n 0) (PRE n n 0 0)))

(rule (=> (and (PRE n m i j) (not (= n 0))
    (= n1 (- n 1))
    (or
        (and (= i1 (+ i 1)) (= j1 j))
        (and (= i1 i) (= j1 (+ j 1)))))
  (PRE n1 m i1 j1)))

(rule (=> (and (PRE n m i j) (= n 0)) (POST1 m i j)))

(rule (=> (and (POST1 m i j ) (not (= i 0)) (= i1 (- i 1)) (= m1 (- m 1)) ) (POST1 m1 i1 j )))

(rule (=> (and (POST1 m i j ) (= i 0)) (POST2 m i j )))

(rule (=> (and (POST2 m i j ) (not (= j 0)) (= j1 (- j 1)) (= m1 (- m 1)) ) (POST2 m1 i j1 )))

(rule (=> (and (POST2 m i j ) (= j 0) (not (= m 0))) fail))

(query fail)
