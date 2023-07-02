(declare-rel FUN (Int Int Int))
(declare-rel SAD (Int Int Int Int))
(declare-var c Int)
(declare-var c1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var N Int)
(declare-var N1 Int)

(declare-rel fail ())

(rule (=> (and (= c 0) (= i 0) (> N 0)) (FUN c i N)))

(rule (=> 
    (and 
      (FUN c i N)
      (< c N)
      (= c1 (+ c 1))
      (= i1 (+ i 2))
    )
    (FUN c1 i1 N)
  )
)

(rule (=> (and (FUN c i N) (>= c N) (= c1 0) (= i1 i) (< N1 N)) (SAD c1 i1 N N1)))

(rule (=>
    (and
        (SAD c i N N1)
        (< c N1)
        (= c1 (+ c 1))
        (= i1 (+ i 1))
    )
    (SAD c1 i1 N N1)
  )
)

(rule (=> (and (SAD c i N N1) (>= c N1) (not (>= i (* 2 N)))) fail))

(query fail)
