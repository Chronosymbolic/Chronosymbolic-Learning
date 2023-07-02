(declare-rel inv (Int Int Int Int))
(declare-var a Int)
(declare-var b Int)
(declare-var c1 Int)
(declare-var c2 Int)
(declare-var d1 Int)
(declare-var d2 Int)

(declare-rel fail ())

(rule (=>
    (and (> a 0) (> b 0) (= c1 0) (= d1 0)) (inv a b c1 d1)
  )
)

(rule (=> 
    (and 
	(inv a b c1 d1)
        (= c2 (+ c1 1))
	(= d2 (+ d1 b))
    )
    (inv a b c2 d2)
  )
)


(rule (=> (and (inv a b c1 d1) (= c1 a) (not (= d1 (* a b)))) fail))


(query fail :print-certificate true)

