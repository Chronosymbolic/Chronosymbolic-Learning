(declare-rel inv (Int Int Int Int))
(declare-var i Int)
(declare-var i1 Int)
(declare-var j Int)
(declare-var j1 Int)
(declare-var k Int)
(declare-var l Int)
(declare-var l1 Int)
(declare-var m Int)

(declare-rel fail ())

(rule (=> (and (= i 0) (> j 0) (> k 0) (= l 0)) (inv i j k l)))

(rule (=> 
    (and 
        (inv i j k l)
        (= i1 (+ i 1))
        (= m (mod j k))
        (= j1 (+ j m))
        (= l1 (+ l m))
    )
    (inv i1 j1 k l1)
  )
)

(rule (=> (and (inv i j k l) (not (<= l (* k i)))) fail))

(query fail :print-certificate true)