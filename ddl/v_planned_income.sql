DROP VIEW IF EXISTS v_planned_income;
CREATE VIEW v_planned_income AS
SELECT
    COALESCE(SUM(CASE WHEN m_mf_category_m_id IN (6, 7) THEN amount END), 0) AS planned_income,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id = 6 THEN amount END), 0) AS planned_income_salary,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id = 7 THEN amount END), 0) AS planned_income_tmp
FROM t_planned_cf t
WHERE DATE_TRUNC('month', t.date) = DATE_TRUNC('month', CURRENT_DATE);