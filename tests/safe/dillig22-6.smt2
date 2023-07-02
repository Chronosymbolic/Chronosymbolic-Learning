(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var k0 Int)
(declare-var k1 Int)
(declare-var N Int)
(declare-var nondet Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 0) (= k1 0)) (inv x1 y1 k1 N)))

(rule (=> 
    (and 
        (inv x0 y0 k0 N)
        (< y0 N)
        (= x1 (ite (= (mod k0 2) 0) (+ x0 nondet) x0))
        (= y1 (+ y0 nondet))
        (= k1 (+ x1 y1))
    )
    (inv x1 y1 k1 N)
  )
)

(rule (=> (and (inv x1 y1 k1 N) (>= y1 N) (not (>= k1 (* 2 N)))) fail))

(query fail :print-certificate true)