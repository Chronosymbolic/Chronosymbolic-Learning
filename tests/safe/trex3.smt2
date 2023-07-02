(declare-rel FUN (Int Int Int Int Int Int Int Int))
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x3 Int)
(declare-var x4 Int)
(declare-var x5 Int)
(declare-var x6 Int)
(declare-var d1 Int)
(declare-var d2 Int)
(declare-var d3 Int)
(declare-var c1 Int)
(declare-var c2 Int)
(declare-var c3 Int)
(declare-var c4 Int)

(declare-rel fail ())

(rule (=> (and (>= x1 0) (>= x2 0) (>= x3 0)
               ( = d1 1) ( = d2 1) ( = d3 1)) (FUN x1 x2 x3 d1 d2 d3 c1 c2)))

(rule (=> 
    (and 
        (FUN x1 x2 x3 d1 d2 d3 c1 c2)
        (> x1 0)
        (> x2 0)
        (> x3 0)
        (= x4 (ite (= c1 1) (- x1 d1) x1))
        (= x5 (ite (and (not (= c1 1)) (= c2 1)) (- x2 d2) x2))
        (= x6 (ite (and (not (= c1 1)) (not (= c2 1))) (- x3 d3) x3))
    )
    (FUN x4 x5 x6 d1 d2 d3 c3 c4)
  )
)

(rule (=> (and (FUN x1 x2 x3 d1 d2 d3 c1 c2) 
               (not (and (> x1 0) (> x2 0) (> x3 0)))
               (not (or (= x1 0) (= x2 0) (= x3 0)))) fail))

(query fail :print-certificate true)

