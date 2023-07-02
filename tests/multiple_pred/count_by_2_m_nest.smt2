(declare-var i1 Int)
(declare-var i0 Int)
(declare-var j1 Int)
(declare-var j0 Int)
(declare-rel itp1 (Int ))
(declare-rel itp2 (Int Int))
(declare-rel fail ())

(rule (itp1 0 ))

(rule (=>
  (and
    (itp1 i0 )
    (< i0 256))
  (itp2 i0 0)
))

(rule (=>
  (and
    (itp2 i0 j0 )
    (< j0 16)
    (= j1 (+ j0 2)))
    (itp2 i0 j1)
  ))

(rule (=>
  (and
    (itp2 i0 j0  )
    (>= j0 16 )
    (= i1 (+ i0 j0))
  )
  (itp1 i1  )
))

(rule (=>
  (and
    (itp1 i0  )
    (>= i0 256 )
    (not (= i0 256 ))
  ) fail))

(query fail :print-certificate true)
