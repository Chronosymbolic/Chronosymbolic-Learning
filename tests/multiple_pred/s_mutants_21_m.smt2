(declare-rel itp1 (Int))
(declare-rel itp2 (Int Int))
(declare-rel itp (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var x3 Int)
(declare-var x4 Int)
(declare-var x5 Int)
(declare-var x6 Int)
(declare-var x9 Int)

(declare-rel fail ())

(rule (=> (> x1 0) (itp1 x1)))

(rule (=> (and (itp1 x1) (not (= x1 0)) (= x2 (- x1 1))) (itp1 x2)))

(rule (=> (and (itp1 x1) (= x1 0) (> x3 0)) (itp2 x1 x3)))

(rule (=> (and (itp2 x1 x3) (not (= x3 0)) (= x4 (- x3 1))) (itp2 x1 x4)))

(rule (=> (and (itp2 x1 x3) (= x3 0) (= x5 (* 10 x9)) (> x9 0) (< x9 10)) (itp x1 x3 x5)))

(rule (=> 
    (and 
        (itp x1 x3 x5)
        (or (and (= x2 (+ x1 1)) (= x4 (- x3 1))) 
            (and (= x2 (- x1 1)) (= x4 (+ x3 1))))
        (= x6 (+ x5 x2 x4))
    )
    (itp x2 x4 x6)
  )
)


(rule (=> (and (itp x1 x3 x5) (= x5 78)) fail))

(query fail)
