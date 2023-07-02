(declare-rel inv1 (Int Int Int))
(declare-rel inv (Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var len Int)
(declare-var len1 Int)

(declare-rel fail ())

(rule (=> (and (= x 0) (= y 0) (>= len 0)) (inv1 x y len)))

(rule (=> (and (inv1 x y len) (= len1 (+ len 1))) (inv1 x y len1)))

(rule (=> (and (inv1 x y len) (= len1 (+ len 80))) (inv x y len1)))

(rule (=> 
    (and 
        (inv x y len)
        (< x len)
        (= x1 (+ x 1))
        (= y1 (+ y 2))
    )
    (inv x1 y1 len)
  )
)


(rule (=> (and (inv x y len) (= x len) (not (= (+ x y) (* 3 len)))) fail))


(query fail :print-certificate true)
