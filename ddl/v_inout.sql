DROP VIEW IF EXISTS v_inout;
CREATE VIEW v_inout AS
SELECT
    m_bym.from_date AS ym,
    SUM(t.amount) AS amount_all,
    SUM(CASE WHEN m_a.m_account_type_id = 1 THEN t.amount END) AS amount_liquid,
    SUM(CASE WHEN m_a.m_account_type_id = 2 THEN t.amount END) AS amount_credit,
    SUM(CASE WHEN m_a.m_account_type_id IN (1,2) THEN t.amount END) AS amount_all_calc,
    SUM(CASE WHEN t.amount > 0 THEN t.amount END) AS amount_income_all,
    SUM(CASE WHEN t.amount > 0 AND m_a.m_account_type_id = 1 THEN t.amount END) AS amount_income_liquid,
    SUM(CASE WHEN t.amount > 0 AND m_a.m_account_type_id = 2 THEN t.amount END) AS amount_income_credit,
    SUM(CASE WHEN t.amount > 0 AND m_a.m_account_type_id IN (1,2) THEN t.amount END) AS amount_income_all_calc,
    SUM(CASE WHEN t.amount < 0 THEN t.amount END) AS amount_outcome_all,
    SUM(CASE WHEN t.amount < 0 AND m_a.m_account_type_id = 1 THEN t.amount END) AS amount_outcome_liquid,
    SUM(CASE WHEN t.amount < 0 AND m_a.m_account_type_id = 2 THEN t.amount END) AS amount_outcome_credit,
    SUM(CASE WHEN t.amount < 0 AND m_a.m_account_type_id IN (1,2) THEN t.amount END) AS amount_outcome_all_calc
FROM m_budget_ym m_bym
LEFT JOIN t_mf_cf t ON t.calc_target AND t.date BETWEEN m_bym.from_date AND m_bym.to_date
LEFT JOIN m_account m_a ON t.m_account_id = m_a.id
GROUP BY m_bym.from_date
ORDER BY from_date;