(declare-rel inv (Bool Bool Bool Bool Int Int Int Int))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Bool)
(declare-var y1 Bool)
(declare-var z Bool)
(declare-var z1 Bool)
(declare-var v Bool)
(declare-var v1 Bool)
(declare-var a Int)
(declare-var a1 Int)
(declare-var b Int)
(declare-var b1 Int)
(declare-var c Int)
(declare-var c1 Int)
(declare-var d Int)
(declare-var d1 Int)

(declare-rel fail ())

(rule (inv x y z v 0 0 0 0))

(rule (=> 
    (and 
        (inv x y z v a b c d)
        (or (and x1 (= a1 (+ a 1)) (= b1 b) (= c1 c) (= d1 d))
            (and y1 (= a1 a) (= b1 (+ b 1)) (= c1 c) (= d1 d))
            (and z1 (= a1 a) (= b1 b) (= c1 (+ c 1)) (= d1 d))
            (and v1 (= a1 a) (= b1 b) (= c1 c) (= d1 (+ d 1))))
    )
    (inv x1 y1 z1 v1 a1 b1 c1 d1)
  )
)

(rule (=> (and (inv x y z v a b c d) (> (+ a b c d) 0) (not (or x y z v))) fail))

(query fail :print-certificate true)