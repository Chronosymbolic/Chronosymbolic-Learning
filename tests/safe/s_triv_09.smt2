(declare-rel inv (Bool Bool))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Bool)
(declare-var y1 Bool)

(declare-rel fail ())

(rule (=> (= y (not x)) (inv x y)))

(rule (=> 
    (and 
        (inv x y)
        (= x1 (not x))
        (= y1 (not y))
    )
    (inv x1 y1)
  )
)

(rule (=> (and (inv true y) y) fail))

(query fail :print-certificate true)