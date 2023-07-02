(declare-rel inv (Int Int Int Int))
(declare-rel inv2 (Int Int Int Int))
(declare-rel inv3 (Int Int Int Int))
(declare-rel inv4 (Int Int Int Int))
(declare-rel inv5 (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var z0 Int)
(declare-var z1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var LRG Int)

(declare-rel fail ())

(rule (=> (and (= x1 0) (= z1 0) (= y1 LRG) (> LRG 0)) (inv x1 y1 z1 LRG)))

(rule (=> 
    (and 
        (inv x0 y0 z0 LRG)
        (< x0 LRG)
        (= x1 (+ x0 1))
        (= z1 (+ z0 1))
        (= y1 (ite (< z0 LRG) y0 (+ y0 1)))
    )
    (inv x1 y1 z1 LRG)
  )
)

(rule (=> (and (inv x0 y0 z0 LRG) (>= x0 LRG)) (inv2 x0 y0 z0 LRG)))

(rule (=>
    (and
        (inv2 x0 y0 z0 LRG)
        (< x0 (* 2 LRG))
        (= x1 (+ x0 1))
        (= z1 (+ z0 1))
        (= y1 (ite (< z0 (* 2 LRG)) y0 (+ y0 1)))
    )
    (inv2 x1 y1 z1 LRG)
  )
)

(rule (=> (and (inv2 x0 y0 z0 LRG) (>= x1 (* 2 LRG))) (inv3 x0 y0 z0 LRG)))

(rule (=>
    (and
        (inv3 x0 y0 z0 LRG)
        (< x0 (* 3 LRG))
        (= x1 (+ x0 1))
        (= z1 (+ z0 1))
        (= y1 (ite (< z0 (* 3 LRG)) y0 (+ y0 1)))
        )
    (inv3 x1 y1 z1 LRG)
  )
)

(rule (=> (and (inv3 x0 y0 z0 LRG) (>= x1 (* 3 LRG))) (inv4 x0 y0 z0 LRG)))

(rule (=>
    (and
        (inv4 x0 y0 z0 LRG)
        (< x0 (* 4 LRG))
        (= x1 (+ x0 1))
        (= z1 (+ z0 1))
        (= y1 (ite (< z0 (* 4 LRG)) y0 (+ y0 1)))
        )
    (inv4 x1 y1 z1 LRG)
  )
)

(rule (=> (and (inv4 x0 y0 z0 LRG) (>= x1 (* 4 LRG))) (inv5 x0 y0 z0 LRG)))

(rule (=>
    (and
        (inv5 x0 y0 z0 LRG)
        (< x0 (* 5 LRG))
        (= x1 (+ x0 1))
        (= z1 (+ z0 1))
        (= y1 (ite (< z0 (* 5 LRG)) y0 (+ y0 1)))
        )
    (inv5 x1 y1 z1 LRG)
  )
)

(rule (=> (and (inv5 x1 y1 z1 LRG) (>= x1 (* 5 LRG)) (not (= y1 LRG))) fail))

(query fail)
