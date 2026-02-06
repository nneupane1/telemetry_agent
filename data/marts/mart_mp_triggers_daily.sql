-- Maintenance Prediction mart for trigger-level events
SELECT
  vin,
  signal_code,
  confidence,
  trigger_time,
  trigger_type
FROM main.predictive_marts.mart_mp_triggers_daily
WHERE trigger_time >= date_sub(current_date(), 14);
