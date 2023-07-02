(declare-rel inv (Int Int Int Int))
(declare-var A Int)
(declare-var B Int)
(declare-var a Int)
(declare-var b Int)
(declare-var a1 Int)
(declare-var b1 Int)

(declare-rel fail ())

(rule (=> (and (> A 0) (> B 0) (= a A) (= b B)) (inv A B a b)))

(rule (=> 
    (and 
        (inv A B a b)
        (not (= a b))
        (= a1 (ite (> a b) (- a b) a))
        (= b1 (ite (not (> a b)) (- b a) b))
    )
    (inv A B a1 b1)
  )
)

(rule (=> (and (inv A B a b) (= a b) (not (and (<= 1 a) (<= a A)))) fail))

(query fail :print-certificate true)

