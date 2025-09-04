DROP VIEW IF EXISTS v_budget_contents;
CREATE VIEW v_budget_contents AS
SELECT
    m_b.title,
    CASE
        WHEN m_b.type = 'mf_category_l' THEN 'MF大項目'
        WHEN m_b.type = 'mf_category_m' THEN 'MF中項目'
    END AS type,
    CASE
        WHEN m_b.type = 'mf_category_l' THEN m_c_l.title
        WHEN m_b.type = 'mf_category_m' THEN ARRAY_TO_STRING(ARRAY_AGG(m_c_m.title), ', ')
    END AS category_title
FROM m_budget m_b
LEFT JOIN m_mf_category_l m_c_l ON m_b.m_mf_category_l_id = m_c_l.id
LEFT JOIN _nc_m2m_m_mf_category_m_m_budget m2m_m_c_m ON m_b.id = m2m_m_c_m.m_budget_id
LEFT JOIN m_mf_category_m m_c_m ON m2m_m_c_m.m_mf_category_m_id = m_c_m.id
GROUP BY m_b.title, m_b.type, m_c_l.title, m_b.display_order
ORDER BY m_b.display_order;