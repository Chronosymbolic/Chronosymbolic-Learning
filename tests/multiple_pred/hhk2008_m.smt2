(declare-rel inv1 (Int Int Int Int))
(declare-rel inv2 (Int Int Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)
(declare-var res0 Int)
(declare-var res1 Int)
(declare-var cnt0 Int)
(declare-var cnt1 Int)

(declare-rel fail ())

(rule (=> (and (<= x1 1000) (<= 0 y1) (<= y1 100) (= res1 x1) (= cnt1 y1)) (inv1 x1 y1 res1 cnt1)))

(rule (=> (and (inv1 x1 y1 res0 cnt0) (= cnt1 (+ cnt0 100)) (= res1 (- res0 100))) (inv2 x1 y1 res1 cnt1)))

(rule (=> 
    (and 
        (inv2 x0 y0 res0 cnt0)
        (> cnt0 0)
        (= cnt1 (- cnt0 1))
        (= res1 (+ res0 1))
    )
    (inv2 x0 y0 res1 cnt1)
  )
)

(rule (=> (inv2 x1 y1 res1 cnt1) (inv1 x1 y1 res1 cnt1)))

(rule (=> (and (inv1 x1 y1 res1 cnt1) (<= cnt1 0) (not (= res1 (+ x1 y1)))) fail))

(query fail :print-certificate true)
