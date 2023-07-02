(declare-rel inv (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var x2 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var y2 Int)
(declare-var n0 Int)
(declare-var n1 Int)
(declare-var flag Int)

(declare-rel fail ())

(rule (=> (and (= x1 1) (= y1 1) (= n0 (ite (= flag 1) 0 1))) (inv x1 y1 n0 flag)))

(rule (=> 
    (and 
        (inv x0 y0 n0 flag)
        (= n1 (ite (= flag 1) (+ x0 y0) (+ x0 y0 1)))
        (= x1 (ite (= flag 1) (+ x0 1) x0))
        (= y1 (ite (= flag 1) y0 (+ y0 1)))
        (= x2 (ite (= (mod n1 2) 1) x1 (+ x1 1)))
        (= y2 (ite (= (mod n1 2) 1) (+ y1 1) y1))
    )
    (inv x2 y2 n1 flag)
  )
)

(rule (=> (and (inv x1 y1 n0 flag) (= n1 (ite (= flag 1) (+ n0 1) n0)) (not (= (mod n1 2) 1))) fail))

(query fail :print-certificate true)