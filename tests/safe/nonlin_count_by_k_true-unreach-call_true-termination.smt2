(declare-var i Int)
(declare-var i_ Int)
(declare-var k Int)
(declare-var LRG Int)
(declare-rel itp (Int Int Int))
(declare-rel fail ())

(rule (=>
  (and
    (<= 0 k)
    (<= k 10)
    (>= LRG 0) 
    (= i 0)
  )
  (itp i k LRG)
))

(rule (=>
  (and
    (itp i_ k LRG)
    (< i_ (* LRG k))
    (= i (+ i_ k))
  )
  (itp i k LRG)
))

(rule (=>
  (and
    (itp i k LRG)
    (not (< i (* LRG k)))  ; stop cond. (redun.)
    (not (= i (* LRG k)))  ; assert negation
  )
  fail
))

(query fail :print-certificate true)
