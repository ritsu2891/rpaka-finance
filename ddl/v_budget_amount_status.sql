DROP VIEW IF EXISTS v_budget_amount_status;
CREATE VIEW v_budget_amount_status AS
WITH
current_ym_cf AS (
    SELECT *
    FROM t_mf_cf t
    WHERE DATE_TRUNC('month', t.date) = DATE_TRUNC('month', CURRENT_DATE)
),
current_ym_recon_planned_cf AS (
    SELECT DISTINCT t_planned_cf_id AS id
    FROM current_ym_cf
),
present_amount AS (
    SELECT
        m_b.id,
        CASE m_b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_cf t
                    WHERE
                        t.calc_target AND
                        t.m_mf_category_l_id = m_b.m_mf_category_l_id
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_cf t
                    WHERE
                        t.calc_target AND
                        t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id )
               )
        END AS present_amount,
        CASE m_b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_cf t
                    LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                    WHERE
                        t.calc_target AND
                        t.m_mf_category_l_id = m_b.m_mf_category_l_id AND
                        m_a.m_account_type_id = 2
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_cf t
                    LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                    WHERE
                        t.calc_target AND
                        t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id ) AND
                        m_a.m_account_type_id = 2
               )
        END AS present_amount_credit
    FROM m_budget m_b
    WHERE m_b.set_amount IS NOT NULL
),
current_ym_planned_cf AS (
    SELECT *
    FROM t_planned_cf t
    LEFT JOIN current_ym_recon_planned_cf c ON c.id = t.id
    WHERE
        DATE_TRUNC('month', t.date) = DATE_TRUNC('month', CURRENT_DATE) AND
        c.id IS NULL
),
planned_amount AS (
    SELECT
        m_b.id,
        CASE m_b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_planned_cf t
                    WHERE t.m_mf_category_l_id = m_b.m_mf_category_l_id
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_planned_cf t
                    WHERE t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id )
               )
        END AS planned_amount,
        CASE m_b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_planned_cf t
                    LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                    WHERE
                        t.m_mf_category_l_id = m_b.m_mf_category_l_id AND
                        m_a.m_account_type_id = 2
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM current_ym_planned_cf t
                    LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                    WHERE
                        t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id ) AND
                        m_a.m_account_type_id = 2
               )
        END AS planned_amount_credit
    FROM m_budget m_b
    WHERE m_b.set_amount IS NOT NULL
)
SELECT
    m_b.title,
    m_b.set_amount,
    COALESCE(p_a.present_amount, 0) AS present_amount,
    m_b.set_amount - COALESCE(p_a.present_amount, 0) AS remaining_amount,
    CASE
        WHEN m_b.set_amount = 0 THEN 0
        ELSE COALESCE(p_a.present_amount, 0) / m_b.set_amount
    END AS ratio_amount,
    COALESCE(p_p.planned_amount, 0) AS planned_amount,
    COALESCE(p_a.present_amount, 0) + COALESCE(p_p.planned_amount, 0) AS present_planned_amount,
    m_b.set_amount - COALESCE(p_a.present_amount, 0) - COALESCE(p_p.planned_amount, 0) AS remaining_planned_amount,
    CASE
        WHEN m_b.set_amount = 0 THEN 0
        ELSE (COALESCE(p_a.present_amount, 0) + COALESCE(p_p.planned_amount, 0)) / m_b.set_amount
    END AS ratio_planned_amount,
    m_b.set_amount_credit,
    COALESCE(p_a.present_amount_credit, 0) AS present_amount_credit,
    m_b.set_amount_credit - COALESCE(p_a.present_amount_credit, 0) AS remaining_amount_credit,
    CASE
        WHEN m_b.set_amount_credit = 0 THEN 0
        ELSE COALESCE(p_a.present_amount_credit, 0) / m_b.set_amount_credit
    END AS ratio_amount_credit,
    COALESCE(p_p.planned_amount_credit, 0) AS planned_amount_credit,
    COALESCE(p_a.present_amount_credit, 0) + COALESCE(p_p.planned_amount_credit, 0) AS present_planned_amount_credit,
    m_b.set_amount_credit - COALESCE(p_a.present_amount_credit, 0) - COALESCE(p_p.planned_amount_credit, 0) AS remaining_planned_amount_credit,
    CASE
        WHEN m_b.set_amount_credit = 0 THEN 0
        ELSE (COALESCE(p_a.present_amount_credit, 0) + COALESCE(p_p.planned_amount_credit, 0)) / m_b.set_amount_credit
    END AS ratio_planned_amount_credit
FROM m_budget m_b
LEFT JOIN present_amount p_a ON p_a.id = m_b.id
LEFT JOIN planned_amount p_p ON p_p.id = m_b.id
WHERE m_b.set_amount IS NOT NULL
ORDER BY m_b.nc_order;