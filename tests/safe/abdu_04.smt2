(declare-rel inv (Int Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var a Int)
(declare-var a1 Int)
(declare-var b Int)
(declare-var b1 Int)
(declare-var len Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= a 0) (= b 0) (>= len 0)) (inv x a b len)))

(rule (=> 
    (and 
        (inv x a b len)
        (= x1 (+ x 1))
        (or
            (and (= a1 (+ a 1)) (= b1 (+ b 2)))
            (and (= a1 (+ a 2)) (= b1 (+ b 1)))
        )
    )
    (inv x1 a1 b1 len)
  )
)

(rule (=> (and (inv x a b len) (not (= (+ a b) (* 3 x)))) fail))

(query fail :print-certificate true)