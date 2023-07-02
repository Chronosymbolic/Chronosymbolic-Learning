(declare-rel FUN (Int Int Int Int Int))
(declare-rel SAD (Int Int))
(declare-var m Int)
(declare-var m1 Int)
(declare-var n Int)
(declare-var n1 Int)
(declare-var s Int)
(declare-var s1 Int)
(declare-var t Int)
(declare-var t1 Int)
(declare-var t2 Int)
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var flag Int)

(declare-rel fail ())

(rule (=> (and (= m 0) (= n 0) (= s 0) (= t 0)) (FUN m n s t flag)))

(rule (=> 
    (and 
        (FUN m n s t flag)
        (= m1 (+ m 1))
        (= n1 (+ n 1))
        (= s1 (+ s m1))
        (= t1 (+ t n1))
        (= t2 (ite (= flag 1) (+ t1 m1) t1))
    )
    (FUN m1 n1 s1 t2 flag)
  )
)

(rule (=> 
    (and 
        (FUN m n s t flag)
        (= x (ite (= flag 1) (+ t (* -2 s) 2) 1))
        (= y 0)
    )
    (SAD x y)
))

(rule (=> 
    (and 
        (SAD x y)
        (<= y x)
        (or (= y1 (+ y 1)) (= y1 (+ y 2)))
    )
    (SAD x y1)
  )
)

(rule (=> (and (SAD x y) (>= y x) (>= y 5)) fail))

(query fail :print-certificate true)

