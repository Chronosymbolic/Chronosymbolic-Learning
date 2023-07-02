(declare-rel inv (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var i Int)
(declare-var i1 Int)

(declare-rel fail ())

(rule (inv x y 100))

(rule (=> 
    (and 
        (inv x y i)
        (= (div x 100) y)
        (= x1 (+ x 101))
        (= y1 (+ y 1))
        (= i1 (- i 1))
    )
    (inv x1 y1 i1)
  )
)

(rule (=> (and (inv x y i) (= (div x 100) y) (< i 0)) fail))

(query fail :print-certificate true)
