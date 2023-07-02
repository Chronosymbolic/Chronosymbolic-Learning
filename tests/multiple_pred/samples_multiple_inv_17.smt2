(declare-rel LOOPX (Int))
(declare-rel LOOPY (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (= x 3138) (LOOPX x)))

(rule (=> (and (LOOPX x) (= y1 0) (= x1 x)) (LOOPY x1 y1)))

(rule (=>
    (and
        (LOOPY x y)
        (not (and (= (mod y 3) 0) (> y 0)))
        (= y1 (+ y 2))
        (= x1 x)
    )
    (LOOPY x1 y1)
  )
)

(rule (=> (and (LOOPY x y) (= (mod y 3) 0) (> y 0) (= x1 (+ x y))) (LOOPX x1)))

(rule (=> (and (LOOPX x) (not (= (mod x 6) 0))) fail))

(query fail)
