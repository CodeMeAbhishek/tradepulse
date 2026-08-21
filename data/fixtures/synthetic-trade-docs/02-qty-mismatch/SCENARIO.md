# SCENARIO — Quantity mismatch (demo climax)
Invoice 500 cartons vs BoL 350 cartons.
Invoice includes `kg_per_unit: 200` so pack→USD/MT price audit can run (not DATA_UNAVAILABLE for missing weight).
Expected: REVIEW_REQUIRED on goods.quantity. Price may PASS/REVIEW vs Yahoo. Safe language only — not fraud.
