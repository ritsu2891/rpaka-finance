DROP VIEW IF EXISTS v_income_total;
CREATE VIEW v_income_total AS
WITH t_cf AS (
    -- 実績収入
    SELECT
        yms.id AS ym_id,
        yms.title AS ym,
        cf.amount,
        cf.m_mf_category_m_id
    FROM m_budget_ym yms
    LEFT JOIN t_mf_cf cf ON
        cf.date BETWEEN yms.from_date AND yms.to_date AND
        cf.m_mf_category_m_id IN (6, 7)
    UNION ALL
    -- 消し込まれていない予定収入
    SELECT
        yms.id AS ym_id,
        yms.title AS ym,
        p_cf.amount,
        p_cf.m_mf_category_m_id
    FROM m_budget_ym yms
    LEFT JOIN t_planned_cf p_cf ON
        p_cf.date BETWEEN yms.from_date AND yms.to_date AND
        p_cf.m_mf_category_m_id IN (6, 7)
    WHERE
        NOT EXISTS (SELECT t_planned_cf_id FROM t_mf_cf WHERE t_planned_cf_id = p_cf.id)
)
SELECT
    ym_id,
    ym,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id IN (6, 7) THEN amount END), 0) AS income,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id = 6 THEN amount END), 0) AS income_salary,
    COALESCE(SUM(CASE WHEN m_mf_category_m_id = 7 THEN amount END), 0) AS income_tmp
FROM t_cf
GROUP BY ym_id, ym
ORDER BY ym_id;