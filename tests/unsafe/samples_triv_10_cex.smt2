(declare-rel itp (Int Int))
(declare-rel itp1 (Int Int))
(declare-rel itp2 (Int Int))
(declare-rel itp3 (Int Int))
(declare-rel itp4 (Int Int))
(declare-rel itp5 (Int Int))
(declare-rel itp6 (Int Int))
(declare-rel itp7 (Int Int))
(declare-rel itp8 (Int Int))
(declare-rel itp9 (Int Int))

(declare-var m Int)
(declare-var m1 Int)
(declare-var i Int)
(declare-var i1 Int)
(declare-var b Int)

(declare-rel fail ())

(rule (=> (and (= m 0) (= i 0)) (itp m i)))

(rule (=> (and (itp m i)
  (= i1 (+ i 234))
  (= m1 (+ m 422)))
(itp1 m1 i1)))

(rule (=> (and (itp1 m i)
  (= i1 (+ i 4552))
  (= m1 (+ m 626)))
(itp2 m1 i1)))

(rule (=> (and (itp2 m i)
  (= i1 (+ i 55525))
  (= m1 (+ m 616)))
(itp3 m1 i1)))

(rule (=> (and (itp3 m i)
  (= i1 (+ i 2455))
  (= m1 (+ m 54566)))
(itp4 m1 i1)))

(rule (=> (and (itp4 m i)
  (= i1 (+ i 1255))
  (= m1 (+ m 758466)))
(itp5 m1 i1)))

(rule (=> (and (itp5 m i)
  (= i1 (+ i 35745))
  (= m1 (+ m 8466)))
(itp6 m1 i1)))

(rule (=> (and (itp6 m i)
  (= i1 (+ i 5845))
  (= m1 (+ m 4)))
(itp7 m1 i1)))

(rule (=> (and (itp7 m i)
  (= i1 (+ i 3595))
  (= m1 (+ m 66)))
(itp8 m1 i1)))

(rule (=> (and (itp8 m i)
  (= i1 (+ i 5845))
  (= m1 (+ m 62796)))
(itp9 m1 i1)))

(rule (=> (and (itp9 m i) true) fail))

(query fail :print-certificate true)

