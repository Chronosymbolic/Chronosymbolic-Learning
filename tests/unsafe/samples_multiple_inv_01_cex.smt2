(declare-rel WRAP (Int))
(declare-rel NEST (Int))
(declare-var m Int)
(declare-var m1 Int)

(declare-rel fail ())

(rule (=>
    (= m 0) (WRAP m)
  )
)

(rule (=> (WRAP m) (NEST m)))

(rule (=> 
    (and 
        (NEST m)
        (= m1 (+ m 1))
    )
    (NEST m1)
  )
)

(rule (=> (NEST m) (WRAP m)))

(rule (=> (and (WRAP m) (not (< m 15))) fail))

(query fail :print-certificate true)

