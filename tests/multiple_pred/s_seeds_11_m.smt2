(declare-rel itp (Int Int))
(declare-rel itp1 (Int Int))
(declare-rel itp2 (Int Int))
(declare-var m Int)
(declare-var m1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var b Int)

(declare-rel fail ())

(rule (=> (and (= m 20) (= i 0)) (itp m i)))

(rule (=> 
    (and 
        (itp m i)
        (> m i)
        (= m1 (+ m 1))
        (= i1 (+ i 1))
    )
    (itp m1 i1)
  )
)


(rule (=> (and (itp m i) (= m1 (+ 20 m))) (itp1 m1 i)))

(rule (=>
    (and
        (itp1 m i)
        (> m i)
        (= m1 (+ m 1))
        (= i1 (+ i 1))
      )
    (itp1 m1 i1)
  )
)

(rule (=> (and (itp1 m i) (= m1 (+ 20 m))) (itp2 m1 i)))

(rule (=>
    (and
        (itp2 m i)
        (> m i)
        (= m1 (+ m 1))
        (= i1 (+ i 1))
      )
    (itp2 m1 i1)
  )
)

(rule (=> (and (itp2 m i) (> i 80) (not (> m 140))) fail))

(query fail)
