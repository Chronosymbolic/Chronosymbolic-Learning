(declare-var i Int)
(declare-var i_ Int)
(declare-var LRG Int)
(declare-rel itp (Int Int))
(declare-rel fail ())

(rule (=>
(and
  (= i 0)
  (= LRG 256))  ; LARGE_INT is large and a power of 2
  (itp i LRG)
))

(rule (=>
  (and
    (itp i_ LRG)
    (< i_ LRG)
    (= i (+ i_ 2))
  )
  (itp i LRG)
))

(rule (=>
  (and
    (itp i LRG)
    (>= i LRG)  ; stop condition (redun.)
    (not (= i LRG))  ; assert negation
  ) fail))

(query fail :print-certificate true)
