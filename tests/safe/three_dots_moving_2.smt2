(declare-rel inv (Int Int Int Int))
(declare-var x Int)
(declare-var x1 Int)
(declare-var y Int)
(declare-var y1 Int)
(declare-var g Int)
(declare-var g1 Int)
(declare-var K Int)

(declare-rel fail ())

(rule (=> (and (< x y)
        (>= g (+ (- K x) (- y x)))
        (>= g (- y x))
        (>= g (- y K)))
    (inv x y K g)))

(rule (=> 
    (and 
        (inv x y K g)
        (= g1 (- g 1))
        (not (= y K))
        (or (and (= x y)
                 (= x1 (ite (> x K) (- x 1) (+ x 1)))
                 (= y1 x1))
            (and (not (= x y))
                 (= x1 x)
                 (= y1 (- y 1))))
    )
    (inv x1 y1 K g1)
  )
)

(rule (=>
    (and
    (inv x y K g)
    (not (= y K)) (not (> g 0)))
  fail))

(query fail)



;	     x    y    K
;-------------------------------------->


;	     x    K    y    
;-------------------------------------->


;	     K    x    y    
;-------------------------------------->
