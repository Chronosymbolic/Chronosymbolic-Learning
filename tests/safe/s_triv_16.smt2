(declare-rel inv (Bool Bool Bool Bool Int))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Bool)
(declare-var y1 Bool)
(declare-var z Bool)
(declare-var z1 Bool)
(declare-var v Bool)
(declare-var v1 Bool)
(declare-var a Int)
(declare-var a1 Int)

(declare-rel fail ())

(rule (inv x y z v 0))

(rule (=> 
    (and 
        (inv x y z v a)
        (=> (= (mod a 4) 0) x1)
        (=> (= (mod a 4) 1) y1)
        (=> (= (mod a 4) 2) z1)
        (=> (= (mod a 4) 3) v1)
        (= a1 (+ a 1))
    )
    (inv x1 y1 z1 v1 a1)
  )
)

(rule (=> (and (inv x y z v a) (> a 0) (not (or x y z v))) fail))

(query fail :print-certificate true)