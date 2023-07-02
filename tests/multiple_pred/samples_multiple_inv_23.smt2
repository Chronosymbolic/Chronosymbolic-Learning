(declare-rel FUN (Int Int Int))
(declare-rel SAD (Int Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var N Int)

(declare-rel fail ())

(rule (=> (and (= i 0) (= j 0) (> N 0)) (FUN i j N)))

(rule (=> 
    (and 
        (FUN i j N)
        (< j N)
        (= i1 (+ i 1))
        (= j1 (+ j 2))
    )
    (FUN i1 j1 N)
  )
)

(rule (=> (and (FUN i j N) (>= j N) (= i1 i) (= j1 1)) (SAD i1 j1 N)))

(rule (=>
    (and
        (SAD i j N)
        (< j N)
        (= i1 (+ i 1))
        (= j1 (+ j 2))
    )
    (SAD i1 j1 N)
  )
)

(rule (=> (and (SAD i j N) (>= j N) (not (= i N))) fail))

(query fail)
