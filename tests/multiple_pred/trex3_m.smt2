(declare-rel FUN (Int Int Int Int Int Int Int Int))
(declare-rel SAD (Int Int Int Int Int Int Int Int Int))
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
(declare-var f1 Int)
(declare-var f2 Int)

(declare-rel fail ())

(rule (=> (and (= d1 1) (= d2 1) (= d3 1)) (FUN x1 x2 x3 d1 d2 d3 c1 c2)))

(rule (=> (and (FUN x1 x2 x3 d1 d2 d3 c1 c2)
               (= x4 (+ x2 22424)) (= x5 (+ x3 7265)) (= x6 (+ x1 94622)))
      (SAD x4 x5 x6 d1 d2 d3 c1 c2 0)))

(rule (=> 
    (and 
        (SAD x1 x2 x3 d1 d2 d3 c1 c2 f1)
        (> x1 0)
        (> x2 0)
        (> x3 0)
        (= x4 (ite (= c1 1) (- x1 d1) x1))
        (= x5 (ite (and (not (= c1 1)) (= c2 1)) (- x2 d2) x2))
        (= x6 (ite (and (not (= c1 1)) (not (= c2 1))) (- x3 d3) x3))
    )
    (SAD x4 x5 x6 d1 d2 d3 c3 c4 1)
  )
)

(rule (=> (and (SAD x1 x2 x3 d1 d2 d3 c1 c2 f1)
        (= f1 0) (not (and (> x1 0) (> x2 0) (> x3 0))))
    (FUN x1 x2 x3 d1 d2 d3 c1 c2)))

(rule (=> (and (SAD x1 x2 x3 d1 d2 d3 c1 c2 f1)
               (= f1 1) (not (and (> x1 0) (> x2 0) (> x3 0)))
               (not (or (= x1 0) (= x2 0) (= x3 0)))) fail))

(query fail)
