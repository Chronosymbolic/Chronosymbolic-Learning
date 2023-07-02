(declare-rel inv (Bool Bool))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Bool)
(declare-var y1 Bool)

(declare-rel fail ())

(rule (=> (and (or (not y) x) (or x y)) (inv x y)))

(rule (=> 
    (and 
        (inv x y)
        (= x1 (not y))
        (= y1 (not x))
    )
    (inv x1 y1)
  )
)

(rule (=> (and (inv x y) x) fail))

(query fail :print-certificate true)