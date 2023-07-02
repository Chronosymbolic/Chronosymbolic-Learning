(declare-rel inv (Int Int Int Int))
(declare-rel inv1 (Int Int Int Int))
(declare-rel inv2 (Int Int Int Int))
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (=> (and (= z1 0) (= x1 0) (= y1 0) (= w1 1))
          (inv z1 x1 y1 w1)))

(rule (=> (inv z0 x0 y0 w0) (inv1 z0 x0 y0 w0)))

(rule (=> (inv1 z0 x0 y0 w0) (inv2 z0 x0 y0 w0)))

(rule (=> 
    (and 
        (inv2 z0 x0 y0 w0)
        (= x1 (ite (= w0 1) (+ x0 1) x0))
        (= w1 (ite (= w0 1) 0 1))
        (= y1 (ite (= z0 0) (+ y0 1) y0))
        (= z1 (ite (= z0 0) 1 0))
    )
    (inv2 z1 x1 y1 w1)
  )
)

(rule (=> (inv2 z0 x0 y0 w0) (inv1 z0 x0 y0 w0)))

(rule (=> (inv1 z0 x0 y0 w0) (inv z0 x0 y0 w0)))

(rule (=> (and (inv z1 x1 y1 w1) (not (= x1 y1))) fail))

(query fail)
