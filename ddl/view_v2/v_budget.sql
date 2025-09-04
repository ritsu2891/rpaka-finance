DROP VIEW IF EXISTS v_budget;
CREATE VIEW v_budget AS
SELECT
    m_bym.from_date AS ym,
    m_b.title,
    CASE m_b.type
        WHEN 'mf_category_l'
            THEN (
                SELECT SUM(amount)
                FROM t_mf_cf t
                WHERE
                    t.calc_target AND
                    t.date BETWEEN m_bym.from_date AND m_bym.to_date AND
                    t.m_mf_category_l_id = m_b.m_mf_category_l_id
           )
        WHEN 'mf_category_m'
            THEN (
                SELECT SUM(amount)
                FROM t_mf_cf t
                WHERE
                    t.calc_target AND
                    t.date BETWEEN m_bym.from_date AND m_bym.to_date AND
                    t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id )
           )
    END AS amount_all,
    CASE m_b.type
        WHEN 'mf_category_l'
            THEN (
                SELECT SUM(amount)
                FROM t_mf_cf t
                LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                WHERE
                    t.calc_target AND
                    t.date BETWEEN m_bym.from_date AND m_bym.to_date AND
                    t.m_mf_category_l_id = m_b.m_mf_category_l_id AND
                    m_a.m_account_type_id = 1
           )
        WHEN 'mf_category_m'
            THEN (
                SELECT SUM(amount)
                FROM t_mf_cf t
                LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                WHERE
                    t.calc_target AND
                    t.date BETWEEN m_bym.from_date AND m_bym.to_date AND
                    t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id ) AND
                    m_a.m_account_type_id = 1
           )
    END AS amount_liquid,
    CASE m_b.type
        WHEN 'mf_category_l'
            THEN (
                SELECT SUM(amount)
                FROM t_mf_cf t
                LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                WHERE
                    t.calc_target AND
                    t.date BETWEEN m_bym.from_date AND m_bym.to_date AND
                    t.m_mf_category_l_id = m_b.m_mf_category_l_id AND
                    m_a.m_account_type_id = 2
           )
        WHEN 'mf_category_m'
            THEN (
                SELECT SUM(amount)
                FROM t_mf_cf t
                LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
                WHERE
                    t.calc_target AND
                    t.date BETWEEN m_bym.from_date AND m_bym.to_date AND
                    t.m_mf_category_m_id IN ( SELECT m_mf_category_m_id FROM _nc_m2m_m_mf_category_m_m_budget m2m WHERE m2m.m_budget_id = m_b.id ) AND
                    m_a.m_account_type_id = 2
           )
    END AS amount_credit
FROM m_budget_ym m_bym
CROSS JOIN m_budget m_b
ORDER BY m_bym.from_date, m_b.display_order;