(declare-rel INV0 (Int Int Int))
(declare-rel INV1 (Int Int Int))
(declare-rel INV2 (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var z Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (> x 0) (INV0 x 0 0)))

(rule (=> (and (INV0 x y z) (> x 0) (= x1 (- x 1))) (INV1 x1 y z)))

(rule (=>
    (and
        (INV1 x y z)
        (< y x)
        (= y1 (+ y 1))
        (= z1 (- z 1))
    )
    (INV1 x y1 z1)
  )
)

(rule (=> (and (INV1 x y z) (not (< y x))) (INV2 x y z)))

(rule (=>
    (and
        (INV2 x y z)
        (< z x)
        (= y1 (- y 1))
        (= z1 (+ z 1))
    )
    (INV2 x y1 z1)
  )
)

(rule (=> (and (INV2 x y z) (not (< z x))) (INV0 x y z)))

(rule (=> (and (INV0 x y z) (= x 0) (not (= y z))) fail))

(query fail)
