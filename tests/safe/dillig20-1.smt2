(declare-rel itp (Int Int Int Int Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var m Int)
(declare-var j Int)
(declare-var k Int)
(declare-var i Int)
(declare-var n Int)
(declare-var x1 Int)
(declare-var y1 Int)
(declare-var m1 Int)
(declare-var j1 Int)

(declare-rel fail ())

(rule (=> (and (= (+ x y) k) (= m 0) (= j 0)) (itp x y m j k i n)))

(rule (=> 
    (and 
        (itp x y m j k i n)
        (< j n)
        (= x1 (ite (= i j) (+ x 1) (- x 1)))
        (= y1 (ite (= i j) (- y 1) (+ y 1)))
        (or (= m1 j) (= m1 m))
        (= j1 (+ j 1))
    )
    (itp x1 y1 m1 j1 k i n)
  )
)


(rule (=> (and (itp x y m j k i n) (= j n) (not (= k (+ x y)))) fail))

(query fail :print-certificate true)

