-- Failure Impact Model mart for root-cause probabilities
SELECT
  vin,
  signal_code,
  confidence,
  observed_at,
  failure_family
FROM main.predictive_marts.mart_fim_rootcause_daily
WHERE observed_at >= date_sub(current_date(), 14);
