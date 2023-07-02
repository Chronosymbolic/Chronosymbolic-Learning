(declare-rel FUN (Int Int Int))
(declare-rel SAD (Int Int Int))
(declare-rel WEE (Int Int Int))
(declare-var k Int)
(declare-var k1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var N Int)

(declare-rel fail ())

(rule (=> (and (= k 0) (= j 0) (> N 0)) (FUN k j N)))

(rule (=> 
    (and 
        (FUN k j N)
        (< j N)
        (= k1 (+ k 1))
        (= j1 (+ j 1))
    )
    (FUN k1 j1 N)
  )
)

(rule (=> (and (FUN k j N) (>= j N) (= k1 k) (= j1 0)) (SAD k1 j1 N)))

(rule (=>
    (and
        (SAD k j N)
        (< j N)
        (= k1 (+ k 1))
        (= j1 (+ j 1))
    )
    (SAD k1 j1 N)
  )
)

(rule (=> (and (SAD k j N) (>= j N) (= k1 k) (= j1 0)) (WEE k1 j1 N)))

(rule (=>
    (and
        (WEE k j N)
        (< j N)
        (= k1 (+ k 1))
        (= j1 (+ j 1))
    )
    (WEE k1 j1 N)
  )
)

(rule (=> (and (WEE k j N) (>= j N) (< k (* 3 N))) fail))

(query fail)
