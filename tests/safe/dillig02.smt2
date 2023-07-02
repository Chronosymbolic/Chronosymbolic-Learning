(declare-rel inv (Int Int Int Int Int Int))
(declare-var i0 Int)
(declare-var i1 Int)
(declare-var j0 Int)
(declare-var j1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var w0 Int)
(declare-var w1 Int)

(declare-rel fail ())

(rule (=> (and (= i1 1) (= j1 0) (= z1 (- i1 j1)) (= x1 0) (= y1 0) (= w1 0))
          (inv i1 j1 z1 x1 y1 w1)))

(rule (=> 
    (and 
        (inv i0 j0 z0 x0 y0 w0)
        (= z1 (+ z0 x0 y0 w0))
        (= y1 (+ y0 1))
        (= x1 (ite (= (mod z1 2) 1) (+ x0 1) x0))
        (= w1 (+ w0 2))
    )
    (inv i0 j0 z1 x1 y1 w1)
  )
)

(rule (=> (and (inv i1 j1 z1 x1 y1 w1) (not (= x1 y1))) fail))

(query fail :print-certificate true)