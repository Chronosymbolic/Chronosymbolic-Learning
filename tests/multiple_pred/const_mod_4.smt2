(declare-rel inv1 (Int Int))
(declare-rel inv3 (Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (= i (* j 3)) (inv1 i j)))

(rule (=> (and (inv1 i j) (= i1 (+ i 1))) (inv3 i1 j)))

(rule (=>
    (and 
        (inv3 i j)
        (= i1 (+ i 3))
        (= j1 (+ j 1)))
    (inv3 i1 j1)))

(rule (=> (and (inv3 i j) (= i1 (+ i 2)) (= j1 j)) (inv1 i1 j1)))

(rule (=> (and (inv1 i j) (not (= (mod i 3) 0))) fail))

(query fail)
