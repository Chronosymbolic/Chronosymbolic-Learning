(declare-rel inv (Bool Bool Bool Bool))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Bool)
(declare-var y1 Bool)
(declare-var z Bool)
(declare-var z1 Bool)
(declare-var v Bool)
(declare-var v1 Bool)

(declare-rel fail ())

(rule (=> (and (= x (not y)) (= z (not v))) (inv x y z v)))

(rule (=> 
    (and 
        (inv x y z v)
        (= x1 (not x))
        (= y1 (not y))
        (= z1 (not z))
        (= v1 (not v))
    )
    (inv x1 y1 z1 v1)
  )
)

(rule (=> (and (inv x y z v) (= y z) (not (= x v))) fail))

(query fail :print-certificate true)