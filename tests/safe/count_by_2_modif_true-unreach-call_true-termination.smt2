(declare-var i Int)
(declare-var i_ Int)
(declare-var c Int)
(declare-var c_ Int)
(declare-var LRG Int)
(declare-rel itp (Int Int Int))
(declare-rel fail ())

(rule (=>
(and
  (= i 0)
  (= c 0)
  (= LRG 256))  ; LARGE_INT is large and a power of 2
  (itp i c LRG)
))

(rule (=>
  (and
    (itp i_ c_ LRG)
    (< i_ LRG)
    (= i (+ i_ 2))
    (= c (+ c_ 1))
  )
  (itp i c LRG)
))

(rule (=>
  (and
    (itp i c LRG)
    (>= i LRG)  ; stop condition (redun.)
    (not (= i LRG))  ; assert negation
  ) fail))

(query fail :print-certificate true)
