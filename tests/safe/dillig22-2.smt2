(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var k0 Int)
(declare-var k1 Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0) (= z1 0) (= k1 0)) (inv x1 y1 z1 k1)))

(rule (=> 
    (and 
        (inv x0 y0 z0 k0)
        (= x1 (ite (= (mod k0 3) 0) (+ x0 1) x0))
        (= y1 (+ y0 1))
        (= z1 (+ z0 1))
        (= k1 (+ x1 y1 z1))
    )
    (inv x1 y1 z1 k1)
  )
)

(rule (=> (and (inv x1 y1 z1 k1) (not (= x1 y1))) fail))

(query fail :print-certificate true)