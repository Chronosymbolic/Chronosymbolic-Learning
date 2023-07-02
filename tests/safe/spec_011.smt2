(declare-rel inv (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var i Int)
(declare-var i1 Int)

(declare-rel fail ())

(rule (=> (and (= i (- y x)) (< x y)) (inv x y i)))

(rule (=>
    (and
        (inv x y i)
        (not (= x y))
        (= x1 (+ x 2))
        (= y1 (+ y 1))
        (= i1 (- i 1))
    )
    (inv x1 y1 i1)
  )
)

(rule (=> (and (inv x y i) (= x y) (not (= i 0))) fail))

(query fail)
