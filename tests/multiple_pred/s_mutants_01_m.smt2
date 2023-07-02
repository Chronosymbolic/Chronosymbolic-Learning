(declare-rel inv1 (Int Int))
(declare-rel inv2 (Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var i Int)
(declare-var i1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= i 0)) (inv1 x i)))

(rule (=> 
    (and 
      (inv1 x i)
      (= i1 (+ i 1))
      (= x1 (+ x i))
    )
    (inv1 x1 i1)
  )
)

(rule (=> (inv1 x i) (inv2 x i)))

(rule (=>
    (and
        (inv2 x i)
        (= i1 (+ i 1))
        (= x1 (+ x i))
    )
    (inv2 x1 i1)
  )
)


(rule (=> (and (inv2 x i) (not (>= x 0))) fail))

(query fail)

