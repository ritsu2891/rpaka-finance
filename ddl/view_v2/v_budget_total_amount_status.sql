DROP VIEW IF EXISTS v_budget_total_amount_status;
CREATE VIEW v_budget_total_amount_status AS
SELECT
    yms.id AS ym_id,
    yms.title AS ym_title,
    SUM(set_amount) AS set_amount,
    SUM(present_amount) AS present_amount,
    SUM(planned_amount) AS planned_amount,
    SUM(present_planned_amount) AS present_planned_amount,
    SUM(GREATEST(set_amount, present_planned_amount)) AS projected_amount,
    SUM(set_amount_credit) AS set_amount_credit,
    SUM(present_amount_credit) AS present_amount_credit,
    SUM(planned_amount_credit) AS planned_amount_credit,
    SUM(present_planned_amount_credit) AS present_planned_amount_credit,
    SUM(GREATEST(set_amount_credit, present_planned_amount_credit)) AS projected_amount_credit
FROM m_budget_ym yms
LEFT JOIN v_budget_amount_status stt ON yms.id = stt.ym_id
GROUP BY yms.id, yms.title
ORDER BY yms.id
;