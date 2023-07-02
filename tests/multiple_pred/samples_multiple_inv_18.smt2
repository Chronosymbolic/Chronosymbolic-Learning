(declare-rel PRE (Int Int Int))
(declare-rel POST (Int Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var z Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (PRE 0 0 z))

(rule (=> (and (PRE i j z)
    (or
        (and (< j 0) (= j1 (- j z)) (= i1 (+ i z)))
        (and (>= j 0) (= j1 (+ j z)) (= i1 (- i z)))))
    (PRE i1 j1 z)))

; z > 0 => j < 0 && i > 0
; z < 0 => j > 0 && i < 0

(rule (=> (and (PRE i j z) (< i j) (= z1 (- z))) (POST i j z1)))

(rule (=> (and (POST i j z) (not (= i j))
    (or
        (and (< j 0) (= j1 (+ i z)) (= i1 (- j z)))
        (and (>= j 0) (= j1 (- i z)) (= i1 (+ j z)))))
    (POST i1 j1 z)))

(rule (=> (and (POST i j z) (= i j) (not (= i 0))) fail))

(query fail)
