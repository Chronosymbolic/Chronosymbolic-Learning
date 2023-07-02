(declare-rel inv (Bool Int))
(declare-var x Bool)
(declare-var x1 Bool)
(declare-var y Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (inv false 865))

(rule (=> 
    (and 
        (inv x y)
        (= y1 (+ (* 248 y) 1324))
    )
    (inv true y1)
  )
)

(rule (=> (and (inv x y) x (not (>= y 214520))) fail))

(query fail :print-certificate true)
