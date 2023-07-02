(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var k0 Int)
(declare-var k1 Int)
(declare-var t0 Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0) (= k1 0)) (inv x1 y1 k1 t0)))

(rule (=> 
    (and 
        (inv x0 y0 k0 t0)
        (< y0 t0)
        (= x1 (ite (= (mod k0 2) 0) (+ x0 1) x0))
        (= y1 (+ y0 1))
        (= k1 (+ x1 y1))
    )
    (inv x1 y1 k1 t0)
  )
)

(rule (=> (and (inv x1 y1 k1 t0) (= y1 t0) (not (= t0 x1))) fail))

(query fail :print-certificate true)