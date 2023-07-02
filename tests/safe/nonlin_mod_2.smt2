(declare-rel inv (Int Int))
(declare-var a Int)
(declare-var b Int)
(declare-var a1 Int)

(declare-rel fail ())

(rule (=> (and (> b 0) (> a 0) (= (mod a b) 0)) (inv a b)))

(rule (=> 
    (and 
	(inv a b)
        (> a b)
        (= a1 (- a b))
    )
    (inv a1 b)
  )
)

(rule (=> (and (inv a b) (not (= (mod a b) 0))) fail))

(query fail :print-certificate true)