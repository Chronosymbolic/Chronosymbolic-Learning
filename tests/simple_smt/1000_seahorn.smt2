(set-info :original "/tmp/sea-nsu6mg/100.pp.ms.o.bc")
(set-info :authors "SeaHorn v.0.1.0-rc3")
(declare-rel verifier.error (Bool Bool Bool ))
(declare-rel main@entry (Int ))
(declare-rel main@.lr.ph (Int Int Int Int ))
(declare-rel main@verifier.error.split ())
(declare-var main@%_9_0 Bool )
(declare-var main@%or.cond.i_0 Bool )
(declare-var main@%_10_0 Bool )
(declare-var main@%_11_0 Bool )
(declare-var main@%_6_0 Int )
(declare-var main@%_7_0 Int )
(declare-var main@%_8_0 Bool )
(declare-var main@%.lcssa11_1 Int )
(declare-var main@%.lcssa10_1 Int )
(declare-var main@%.lcssa_1 Int )
(declare-var main@%c.0.i3_2 Int )
(declare-var main@%a.0.i2_2 Int )
(declare-var main@%b.0.i1_2 Int )
(declare-var main@%_0_0 Int )
(declare-var main@%_1_0 Int )
(declare-var main@%_2_0 Bool )
(declare-var @unknown_0 Int )
(declare-var main@entry_0 Bool )
(declare-var main@.lr.ph.preheader_0 Bool )
(declare-var main@.lr.ph_0 Bool )
(declare-var main@%c.0.i3_0 Int )
(declare-var main@%a.0.i2_0 Int )
(declare-var main@%b.0.i1_0 Int )
(declare-var main@%c.0.i3_1 Int )
(declare-var main@%a.0.i2_1 Int )
(declare-var main@%b.0.i1_1 Int )
(declare-var main@verifier.error_0 Bool )
(declare-var main@%c.0.i.lcssa_0 Int )
(declare-var main@%a.0.i.lcssa_0 Bool )
(declare-var main@%b.0.i.lcssa_0 Int )
(declare-var main@%c.0.i.lcssa_1 Int )
(declare-var main@%a.0.i.lcssa_1 Bool )
(declare-var main@%b.0.i.lcssa_1 Int )
(declare-var main@verifier.error.split_0 Bool )
(declare-var main@%_3_0 Int )
(declare-var main@%_4_0 Int )
(declare-var main@%_5_0 Int )
(declare-var main@.lr.ph_1 Bool )
(declare-var main@.verifier.error_crit_edge_0 Bool )
(declare-var main@%.lcssa11_0 Int )
(declare-var main@%.lcssa10_0 Int )
(declare-var main@%.lcssa_0 Int )
(declare-var main@%phitmp_0 Bool )
(rule (verifier.error false false false))
(rule (verifier.error false true true))
(rule (verifier.error true false true))
(rule (verifier.error true true true))
(rule (main@entry @unknown_0))
(rule (=> (and (main@entry @unknown_0)
         true
         (= main@%_0_0 @unknown_0)
         (= main@%_2_0 (= main@%_1_0 0))
         (=> main@.lr.ph.preheader_0 (and main@.lr.ph.preheader_0 main@entry_0))
         (=> (and main@.lr.ph.preheader_0 main@entry_0) (not main@%_2_0))
         (=> main@.lr.ph_0 (and main@.lr.ph_0 main@.lr.ph.preheader_0))
         main@.lr.ph_0
         (=> (and main@.lr.ph_0 main@.lr.ph.preheader_0) (= main@%c.0.i3_0 0))
         (=> (and main@.lr.ph_0 main@.lr.ph.preheader_0) (= main@%a.0.i2_0 0))
         (=> (and main@.lr.ph_0 main@.lr.ph.preheader_0) (= main@%b.0.i1_0 0))
         (=> (and main@.lr.ph_0 main@.lr.ph.preheader_0)
             (= main@%c.0.i3_1 main@%c.0.i3_0))
         (=> (and main@.lr.ph_0 main@.lr.ph.preheader_0)
             (= main@%a.0.i2_1 main@%a.0.i2_0))
         (=> (and main@.lr.ph_0 main@.lr.ph.preheader_0)
             (= main@%b.0.i1_1 main@%b.0.i1_0)))
    (main@.lr.ph main@%a.0.i2_1 main@%b.0.i1_1 main@%c.0.i3_1 @unknown_0)))
(rule (let ((a!1 (and (main@entry @unknown_0)
                true
                (= main@%_0_0 @unknown_0)
                (= main@%_2_0 (= main@%_1_0 0))
                (=> main@verifier.error_0
                    (and main@verifier.error_0 main@entry_0))
                (=> (and main@verifier.error_0 main@entry_0) main@%_2_0)
                (=> (and main@verifier.error_0 main@entry_0)
                    (= main@%c.0.i.lcssa_0 0))
                (=> (and main@verifier.error_0 main@entry_0)
                    (= main@%a.0.i.lcssa_0 true))
                (=> (and main@verifier.error_0 main@entry_0)
                    (= main@%b.0.i.lcssa_0 0))
                (=> (and main@verifier.error_0 main@entry_0)
                    (= main@%c.0.i.lcssa_1 main@%c.0.i.lcssa_0))
                (=> (and main@verifier.error_0 main@entry_0)
                    (= main@%a.0.i.lcssa_1 main@%a.0.i.lcssa_0))
                (=> (and main@verifier.error_0 main@entry_0)
                    (= main@%b.0.i.lcssa_1 main@%b.0.i.lcssa_0))
                (=> main@verifier.error_0
                    (= main@%_9_0 (= main@%b.0.i.lcssa_1 main@%c.0.i.lcssa_1)))
                (=> main@verifier.error_0
                    (= main@%or.cond.i_0 (or main@%a.0.i.lcssa_1 main@%_9_0)))
                (=> main@verifier.error_0 (not main@%or.cond.i_0))
                (=> main@verifier.error_0
                    (= main@%_10_0 (xor main@%a.0.i.lcssa_1 true)))
                (=> main@verifier.error_0 (= main@%_11_0 (xor main@%_9_0 true)))
                (=> main@verifier.error.split_0
                    (and main@verifier.error.split_0 main@verifier.error_0))
                main@verifier.error.split_0)))
  (=> a!1 main@verifier.error.split)))
(rule (=> (and (main@.lr.ph main@%a.0.i2_0 main@%b.0.i1_0 main@%c.0.i3_0 @unknown_0)
         true
         (= main@%_3_0 (+ main@%a.0.i2_0 1))
         (= main@%_4_0 (+ main@%b.0.i1_0 1))
         (= main@%_5_0 (+ main@%c.0.i3_0 1))
         (= main@%_6_0 @unknown_0)
         (= main@%_8_0 (= main@%_7_0 0))
         (=> main@.lr.ph_1 (and main@.lr.ph_1 main@.lr.ph_0))
         main@.lr.ph_1
         (=> (and main@.lr.ph_1 main@.lr.ph_0) (not main@%_8_0))
         (=> (and main@.lr.ph_1 main@.lr.ph_0) (= main@%c.0.i3_1 main@%_5_0))
         (=> (and main@.lr.ph_1 main@.lr.ph_0) (= main@%a.0.i2_1 main@%_3_0))
         (=> (and main@.lr.ph_1 main@.lr.ph_0) (= main@%b.0.i1_1 main@%_4_0))
         (=> (and main@.lr.ph_1 main@.lr.ph_0)
             (= main@%c.0.i3_2 main@%c.0.i3_1))
         (=> (and main@.lr.ph_1 main@.lr.ph_0)
             (= main@%a.0.i2_2 main@%a.0.i2_1))
         (=> (and main@.lr.ph_1 main@.lr.ph_0)
             (= main@%b.0.i1_2 main@%b.0.i1_1)))
    (main@.lr.ph main@%a.0.i2_2 main@%b.0.i1_2 main@%c.0.i3_2 @unknown_0)))
(rule (let ((a!1 (and (main@.lr.ph main@%a.0.i2_0
                             main@%b.0.i1_0
                             main@%c.0.i3_0
                             @unknown_0)
                true
                (= main@%_3_0 (+ main@%a.0.i2_0 1))
                (= main@%_4_0 (+ main@%b.0.i1_0 1))
                (= main@%_5_0 (+ main@%c.0.i3_0 1))
                (= main@%_6_0 @unknown_0)
                (= main@%_8_0 (= main@%_7_0 0))
                (=> main@.verifier.error_crit_edge_0
                    (and main@.verifier.error_crit_edge_0 main@.lr.ph_0))
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    main@%_8_0)
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    (= main@%.lcssa11_0 main@%_5_0))
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    (= main@%.lcssa10_0 main@%_4_0))
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    (= main@%.lcssa_0 main@%_3_0))
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    (= main@%.lcssa11_1 main@%.lcssa11_0))
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    (= main@%.lcssa10_1 main@%.lcssa10_0))
                (=> (and main@.verifier.error_crit_edge_0 main@.lr.ph_0)
                    (= main@%.lcssa_1 main@%.lcssa_0))
                (=> main@.verifier.error_crit_edge_0
                    (= main@%phitmp_0 (< main@%.lcssa_1 1000)))
                (=> main@verifier.error_0
                    (and main@verifier.error_0 main@.verifier.error_crit_edge_0))
                (=> (and main@verifier.error_0 main@.verifier.error_crit_edge_0)
                    (= main@%c.0.i.lcssa_0 main@%.lcssa11_1))
                (=> (and main@verifier.error_0 main@.verifier.error_crit_edge_0)
                    (= main@%a.0.i.lcssa_0 main@%phitmp_0))
                (=> (and main@verifier.error_0 main@.verifier.error_crit_edge_0)
                    (= main@%b.0.i.lcssa_0 main@%.lcssa10_1))
                (=> (and main@verifier.error_0 main@.verifier.error_crit_edge_0)
                    (= main@%c.0.i.lcssa_1 main@%c.0.i.lcssa_0))
                (=> (and main@verifier.error_0 main@.verifier.error_crit_edge_0)
                    (= main@%a.0.i.lcssa_1 main@%a.0.i.lcssa_0))
                (=> (and main@verifier.error_0 main@.verifier.error_crit_edge_0)
                    (= main@%b.0.i.lcssa_1 main@%b.0.i.lcssa_0))
                (=> main@verifier.error_0
                    (= main@%_9_0 (= main@%b.0.i.lcssa_1 main@%c.0.i.lcssa_1)))
                (=> main@verifier.error_0
                    (= main@%or.cond.i_0 (or main@%a.0.i.lcssa_1 main@%_9_0)))
                (=> main@verifier.error_0 (not main@%or.cond.i_0))
                (=> main@verifier.error_0
                    (= main@%_10_0 (xor main@%a.0.i.lcssa_1 true)))
                (=> main@verifier.error_0 (= main@%_11_0 (xor main@%_9_0 true)))
                (=> main@verifier.error.split_0
                    (and main@verifier.error.split_0 main@verifier.error_0))
                main@verifier.error.split_0)))
  (=> a!1 main@verifier.error.split)))
(query main@verifier.error.split)

