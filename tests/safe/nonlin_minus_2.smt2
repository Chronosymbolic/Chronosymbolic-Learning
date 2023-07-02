(declare-rel inv (Int Int Int Int))
(declare-var a Int)
(declare-var b Int)
(declare-var c Int)
(declare-var d Int)
(declare-var c1 Int)
(declare-var d1 Int)

(declare-rel fail ())

(rule (=> (and (> a 0) (> b 0) (= c 0) (= d a)) (inv a b c d)))

(rule (=> 
    (and 
        (inv a b c d)
        (>= d b)
        (= c1 (+ c 1))
        (= d1 (- d b))
    )
    (inv a b c1 d1)
  )
)


(rule (=> (and (inv a b c d) (< c b) (not (= a (+ (* b c) d)))) fail))


(query fail :print-certificate true)

