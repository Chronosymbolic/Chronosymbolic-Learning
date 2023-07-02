(declare-var i1 Int)
(declare-var i0 Int)
(declare-var LRG1 Int)
(declare-var LRG2 Int)
(declare-rel itp1 (Int Int))
(declare-rel itp2 (Int Int ))
(declare-rel fail ())

(rule (=>
  (and
    (= i1 0)
    (= LRG1 128))
    (itp1 i1 LRG1)
  ))

(rule (=>
  (and
    (itp1 i0 LRG1)
    (< i0 LRG1)
    (= i1 (+ i0 2))
  )
  (itp1 i1 LRG1)
))

(rule (=>
  (and
    (itp1 i0 LRG1)
    (>= i0 LRG1)
    (= LRG2 (+ LRG1 128)))
    (itp2 i0 LRG2 )
  ))

(rule (=>
  (and
    (itp2 i0 LRG1 )
    (< i0 LRG1 )
    (= i1 (+ i0 2))
  )
  (itp2 i1 LRG1 )
))

(rule (=>
  (and
    (itp2 i1 LRG1 )
    (>= i1  LRG1 )
    (not (= i1 LRG1 ))
  ) fail))

(query fail :print-certificate true)
