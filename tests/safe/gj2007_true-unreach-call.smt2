(declare-rel inv (Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var LRG Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= y1 LRG) (> LRG 0)) (inv x1 y1 LRG)))

(rule (=> 
    (and 
        (inv x0 y0 LRG)
        (< x0 (* 2 LRG))
        (= x1 (+ x0 1))
        (= y1 (ite (< x0 LRG) y0 (+ y0 1)))
    )
    (inv x1 y1 LRG)
  )
)

(rule (=> (and (inv x1 y1 LRG) (>= x1 (* 2 LRG)) (not (= y1 (* 2 LRG)))) fail))

(query fail :print-certificate true)