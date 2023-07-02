(declare-rel inv (Int Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var g Int)
(declare-var g1 Int)
(declare-var K Int)

(declare-rel fail ())

(rule (=> (and
        (>= g (- x K))
        (>= g (- K x))
        (>= g (- y K))
        (>= g (- K y))
        (>= g (- y x))
        (>= g (- x y)))
    (inv x y K g)))

(rule (=> 
    (and 
        (inv x y K g)
        (= g1 (- g 1))
        (not (= y K))
        (= x1 (ite (> x K) (- x 1) (ite (< x K) (+ x 1) x)))
        (= y1 (ite (> y x1) (- y 1) (ite (< y x1) (+ y 1) y)))
    )
    (inv x1 y1 K g1)
  )
)

(rule (=>
    (and
    (inv x y K g)
    (not (= y K)) (not (> g 0)))
  fail))

(query fail)
