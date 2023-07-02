(declare-rel FUN (Int Int Int Int))
(declare-var x Int)
(declare-var y Int)
(declare-var lock Int)
(declare-var input Int)
(declare-var x2 Int)
(declare-var y2 Int)
(declare-var lock2 Int)
(declare-var input2 Int)

(declare-rel fail ())

(rule (=> (and (= lock (ite (= input 1) 0 1)) (= x y) (= y2 (ite (= input 1) (+ y 1) y)))
          (FUN x y2 lock input)))

(rule (=> 
    (and 
        (FUN x y lock input)
        (not (= x y))
        (= lock2 (ite (= input2 1) 0 1)) (= x2 y) (= y2 (ite (= input2 1) (+ y 1) y))
    )
    (FUN x2 y2 lock2 input2)
  )
)

(rule (=> (and (FUN x y lock input) (= x y) (not (= lock 1))) fail))

(query fail :print-certificate true)

