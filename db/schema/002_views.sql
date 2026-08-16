-- Analytical views for the DSE pollution correlation agent.

CREATE OR REPLACE VIEW v_exam_calendar AS
SELECT
    year,
    CAST(exam_date AS DATE) AS exam_date,
    date_text_en,
    date_text_zh,
    subject_en,
    subject_zh,
    paper,
    time_start,
    time_end,
    is_reserve
FROM written_papers
WHERE exam_date IS NOT NULL
  AND COALESCE(is_reserve, FALSE) = FALSE;

CREATE OR REPLACE VIEW v_category_a_performance AS
SELECT
    year,
    candidate_type,
    subject_group_en,
    subject_en,
    subject_zh,
    gender,
    is_summary,
    n_entered,
    n_sat,
    chinese_version_pct,
    n_5ss,
    pct_5ss,
    n_5_plus,
    pct_5_plus,
    n_4_plus,
    pct_4_plus,
    n_u,
    pct_u
FROM category_a_subject_results;

CREATE OR REPLACE VIEW v_exam_day_environment AS
SELECT
    e.year,
    e.exam_date,
    e.subject_en,
    e.subject_zh,
    e.paper,
    e.time_start,
    e.time_end,
    a.mean_aqhi AS city_mean_aqhi,
    a.max_aqhi AS city_max_aqhi,
    a.hours_reported AS aqhi_hours_reported,
    w.direction_deg AS wind_direction_deg,
    w.completeness AS wind_completeness
FROM v_exam_calendar e
LEFT JOIN air_quality_daily_city a ON e.exam_date = a.date
LEFT JOIN wind_direction_daily w ON e.exam_date = w.date;

CREATE OR REPLACE VIEW v_subject_year_aqhi AS
SELECT
    p.year,
    p.candidate_type,
    p.subject_en,
    p.gender,
    p.n_sat,
    p.pct_5_plus,
    p.pct_u,
    AVG(e.city_mean_aqhi) AS avg_exam_day_mean_aqhi,
    COUNT(e.exam_date) AS exam_sittings_with_aqhi
FROM v_category_a_performance p
JOIN v_exam_day_environment e
  ON p.year = e.year
 AND p.subject_en = e.subject_en
WHERE p.gender = 'total'
  AND COALESCE(p.is_summary, FALSE) = FALSE
GROUP BY
    p.year,
    p.candidate_type,
    p.subject_en,
    p.gender,
    p.n_sat,
    p.pct_5_plus,
    p.pct_u;
