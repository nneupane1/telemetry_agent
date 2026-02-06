-- Machine Health mart for VIN-level anomaly evidence
-- Source: Unity Catalog tables containing normalized HI signals.
SELECT
  vin,
  hi_code,
  confidence,
  observed_at,
  health_index
FROM main.predictive_marts.mart_mh_hi_snapshot_daily
WHERE observed_at >= date_sub(current_date(), 14);
