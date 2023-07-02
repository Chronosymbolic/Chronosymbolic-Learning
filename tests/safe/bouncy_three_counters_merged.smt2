(declare-rel itp1 (Int Int Int Int))

(declare-var count1 Int)
(declare-var count2 Int)
(declare-var count3 Int)
(declare-var count4 Int)
(declare-var count5 Int)
(declare-var count6 Int)
(declare-var z1 Int)
(declare-var z2 Int)

(declare-rel fail ())

(rule (=> (and (= count1 count3) (= count1 count5) (= count3 0) (= z1 count1)) (itp1 count1 count3 count5 z1)))

(rule (=>
    (and
        (itp1 count1 count3 count5 z1)
        (or
            (and (= count2 (+ count1 1)) (= count4 count3) (= count6 count5) (= z2 (+ z1 1)))
            (and (= count4 (+ count3 1)) (= count2 count1) (= count6 count5) (= z2 (- z1 1)))
            (and (= count6 (+ count5 1)) (= count2 count1) (= count4 count3) (= z2 (+ z1 1)))
	)
    )
    (itp1 count2 count4 count6 z2)
  )
)

(rule (=> (and (itp1 count1 count3 count5 z1) (= count1 count3) (= count1 count5) (not (= z1 count1))) fail))

(query fail :print-certificate true)