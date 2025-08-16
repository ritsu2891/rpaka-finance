DROP VIEW IF EXISTS v_income_total;
CREATE VIEW v_income_total AS
WITH t_cf AS (
    SELECT
        t_mf_cf.amount,
        t_mf_cf.m_mf_category_m_id
    FROM t_mf_cf
    LEFT JOIN t_planned_cf ON t_planned_cf.id = t_mf_cf.t_planned_cf_id
    WHERE
        DATE_TRUNC('month', t_mf_cf.date) = DATE_TRUNC('month', CURRENT_DATE) AND
        t_mf_cf.m_mf_category_m_id IN (6, 7) AND
        t_mf_cf.t_planned_cf_id IS NULL
    UNION ALL
    SELECT
        t_planned_cf.amount,
        t_planned_cf.m_mf_category_m_id
    FROM t_planned_cf
    LEFT JOIN t_mf_cf ON t_planned_cf.id = t_mf_cf.t_planned_cf_id
    WHERE
        DATE_TRUNC('month', t_planned_cf.date) = DATE_TRUNC('month', CURRENT_DATE) AND
        t_planned_cf.m_mf_category_m_id IN (6, 7) AND
        t_mf_cf.id IS NULL
)
SELECT
    COALESCE(SUM(CASE WHEN m_mf_category_m_id IN (6, 7) THEN amount END), 0) AS income,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id = 6 THEN amount END), 0) AS income_salary,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id = 7 THEN amount END), 0) AS income_tmp
FROM t_cf;