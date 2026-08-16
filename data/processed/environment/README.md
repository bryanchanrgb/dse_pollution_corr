# Environment tables

## air_quality_hourly
One row per date × hour × monitoring station. `aqhi` is the Air Quality Health Index (1–10+).

## air_quality_daily
Daily mean/max AQHI per station.

## air_quality_daily_city
City-wide daily mean/max AQHI (average across stations with readings that day). Use this to join exam dates.

## wind_direction_daily
Daily prevailing wind direction (degrees) at King's Park. `completeness` is `C` (complete) or `#` (partial).
