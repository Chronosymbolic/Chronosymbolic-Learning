(declare-rel itp (Int Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var len Int)

(declare-rel fail ())

(rule (=> (and (>= x 0) (>= y 0) (< y x) (= len x) (= i 0)) (itp x y i len)))

(rule (=> 
    (and 
        (itp x y i len)
        (< i y)
        (= i1 (+ i 1))
    )
    (itp x1 y i1 len)
  )
)


(rule (=> (and (itp x y i len) (< i y) (or (< i 0) (>= i len))) fail))


(query fail :print-certificate true)

