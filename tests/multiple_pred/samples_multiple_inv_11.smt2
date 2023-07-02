(declare-rel LOOPY (Int Int))
(declare-rel LOOPZ (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var z Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (< y z) (LOOPY y z)))

(rule (=>
    (and
        (LOOPY y z)
        (< y z)
        (= y1 (+ y 1000))
        (= z1 z)
    )
    (LOOPY y1 z1)
  )
)

(rule (=> (and (LOOPY y z) (not (< y z))) (LOOPZ 0 y z)))

(rule (=>
    (and
        (LOOPZ x y z)
        (> y z)
        (= x1 (+ x 1))
        (= y1 y)
        (= z1 (+ z 2))
    )
    (LOOPZ x1 y1 z1)
  )
)

(rule (=> (and (LOOPZ x y z) (not (> y z)) (not (<= x 500))) fail))

(query fail)
