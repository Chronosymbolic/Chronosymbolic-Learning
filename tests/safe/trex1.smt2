(declare-rel FUN (Int Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var k Int)
(declare-var z Int)
(declare-var z1 Int)

(declare-rel fail ())

(rule (=> (and (= x 1) (= y 1) (= k 1) (= z 1)) (FUN x y k z)))

(rule (=> 
    (and 
        (FUN x y k z)
        (< z k)
        (= z1 (* 2 z))
    )
    (FUN x y k z1)
  )
)

(rule (=> (and (FUN x y k z) (>= z k) (not (>= z 1))) fail))

(query fail :print-certificate true)

