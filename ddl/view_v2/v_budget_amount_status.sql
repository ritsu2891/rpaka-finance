DROP VIEW IF EXISTS v_budget_amount_status;
CREATE VIEW v_budget_amount_status AS
WITH
ym_budget AS (
    -- 予算年月×予算項目
    SELECT
        ym.id AS ym_id,
        ym.title AS ym,
        ym.from_date,
        ym.to_date,
        b.id AS budget_id,
        b.title,
        b.type,
        b.m_mf_category_l_id,
        b.set_amount,
        b.set_amount_credit,
        b.display_order
    FROM m_budget_ym ym
    CROSS JOIN m_budget b
    WHERE b.set_amount IS NOT NULL
),
recon_planned_cf AS (
    -- 消し込み済みの予定入出金ID
    SELECT DISTINCT t_planned_cf_id
    FROM t_mf_cf
    WHERE t_planned_cf_id IS NOT NULL
),
present_amount AS (
    -- 確定支出額
    SELECT
        b.ym_id,
        b.budget_id,
        CASE b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM v_budget_cf cf
                    WHERE
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_l_id = b.m_mf_category_l_id
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM v_budget_cf cf
                    WHERE
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = b.budget_id)
               )
        END AS present_amount,
        CASE b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM v_budget_cf cf
                    LEFT JOIN m_account m_a ON cf.m_account_id = m_a.id
                    WHERE
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_l_id = b.m_mf_category_l_id AND
                        m_a.m_account_type_id = 2
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM v_budget_cf cf
                    LEFT JOIN m_account m_a ON cf.m_account_id = m_a.id
                    WHERE
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = b.budget_id ) AND
                        m_a.m_account_type_id = 2
               )
        END AS present_amount_credit
    FROM ym_budget b
    WHERE b.set_amount IS NOT NULL
),
planned_amount AS (
    -- 予定支出額
    SELECT
        b.ym_id,
        b.budget_id,
        CASE b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM t_planned_cf cf
                    LEFT JOIN recon_planned_cf rp_cf ON cf.id = rp_cf.t_planned_cf_id
                    WHERE
                        rp_cf.t_planned_cf_id IS NULL AND
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_l_id = b.m_mf_category_l_id
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM t_planned_cf cf
                    LEFT JOIN recon_planned_cf rp_cf ON cf.id = rp_cf.t_planned_cf_id
                    WHERE
                        rp_cf.t_planned_cf_id IS NULL AND
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_m_id IN (
                            SELECT m_mf_category_m_id
                            FROM _nc_m2m_m_mf_category_m_m_budget m2m
                            WHERE m2m.m_budget_id = b.budget_id
                        )
               )
        END AS planned_amount,
        CASE b.type
            WHEN 'mf_category_l'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM t_planned_cf cf
                    LEFT JOIN recon_planned_cf rp_cf ON cf.id = rp_cf.t_planned_cf_id
                    LEFT JOIN m_account m_a ON cf.m_account_id = m_a.id
                    WHERE
                        rp_cf.t_planned_cf_id IS NULL AND
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_l_id = b.m_mf_category_l_id AND
                        m_a.m_account_type_id = 2
               )
            WHEN 'mf_category_m'
                THEN (
                    SELECT ABS(SUM(amount))
                    FROM t_planned_cf cf
                    LEFT JOIN recon_planned_cf rp_cf ON cf.id = rp_cf.t_planned_cf_id
                    LEFT JOIN m_account m_a ON cf.m_account_id = m_a.id
                    WHERE
                        rp_cf.t_planned_cf_id IS NULL AND
                        cf.date BETWEEN b.from_date AND b.to_date AND
                        cf.m_mf_category_m_id IN (
                            SELECT m_mf_category_m_id
                            FROM _nc_m2m_m_mf_category_m_m_budget m2m
                            WHERE m2m.m_budget_id = b.budget_id
                        ) AND
                        m_a.m_account_type_id = 2
               )
        END AS planned_amount_credit
    FROM ym_budget b
    WHERE b.set_amount IS NOT NULL
)
SELECT
    b.ym_id,
    b.ym,
    b.budget_id,
    b.title,
    b.set_amount,
    COALESCE(p_a.present_amount, 0) AS present_amount,
    b.set_amount - COALESCE(p_a.present_amount, 0) AS remaining_amount,
    CASE
        WHEN b.set_amount = 0 THEN 0
        ELSE COALESCE(p_a.present_amount, 0) / b.set_amount
    END AS ratio_amount,
    COALESCE(p_p.planned_amount, 0) AS planned_amount,
    COALESCE(p_a.present_amount, 0) + COALESCE(p_p.planned_amount, 0) AS present_planned_amount,
    b.set_amount - COALESCE(p_a.present_amount, 0) - COALESCE(p_p.planned_amount, 0) AS remaining_planned_amount,
    CASE
        WHEN b.set_amount = 0 THEN 0
        ELSE (COALESCE(p_a.present_amount, 0) + COALESCE(p_p.planned_amount, 0)) / b.set_amount
    END AS ratio_planned_amount,
    b.set_amount_credit,
    COALESCE(p_a.present_amount_credit, 0) AS present_amount_credit,
    b.set_amount_credit - COALESCE(p_a.present_amount_credit, 0) AS remaining_amount_credit,
    CASE
        WHEN b.set_amount_credit = 0 THEN 0
        ELSE COALESCE(p_a.present_amount_credit, 0) / b.set_amount_credit
    END AS ratio_amount_credit,
    COALESCE(p_p.planned_amount_credit, 0) AS planned_amount_credit,
    COALESCE(p_a.present_amount_credit, 0) + COALESCE(p_p.planned_amount_credit, 0) AS present_planned_amount_credit,
    b.set_amount_credit - COALESCE(p_a.present_amount_credit, 0) - COALESCE(p_p.planned_amount_credit, 0) AS remaining_planned_amount_credit,
    CASE
        WHEN b.set_amount_credit = 0 THEN 0
        ELSE (COALESCE(p_a.present_amount_credit, 0) + COALESCE(p_p.planned_amount_credit, 0)) / b.set_amount_credit
    END AS ratio_planned_amount_credit
FROM ym_budget b
LEFT JOIN present_amount p_a ON p_a.budget_id = b.budget_id AND p_a.ym_id = b.ym_id
LEFT JOIN planned_amount p_p ON p_p.budget_id = b.budget_id AND p_p.ym_id = b.ym_id
WHERE b.set_amount IS NOT NULL
ORDER BY b.from_date, b.display_order;