(declare-rel inv1 (Int Int))
(declare-rel inv (Int Int Int Int))

(declare-var z0 Int)
(declare-var z1 Int)
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (inv1 0 0))

(rule (=> (and (inv1 x0 y0 ) (= x1 (+ y0 1534)) (= y1 (+ x0 1534))) (inv1 x1 y1 )))

(rule (=> (and (inv1 x0 y0 ) (= z1 0) (= w1 1)) (inv z1 x0 y0 w1)))

(rule (=> 
    (and 
        (inv z0 x0 y0 w0)
        (= x1 (ite (= w0 0) x0 (+ x0 1)))
        (= w1 (ite (= w0 0) w0 (- 1 w0)))
        (= y1 (ite (= z0 0) (+ y0 1) y0))
        (= z1 (ite (= z0 0) 1 z0))
    )
    (inv z1 x1 y1 w1)
  )
)

(rule (=> (and (inv z1 x1 y1 w1) (not (= x1 y1))) fail))

(query fail)
