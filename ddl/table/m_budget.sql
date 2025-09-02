-- 予算項目マスタ
DROP TABLE IF EXISTS m_budget;
CREATE TABLE m_budget
(
    id                 SERIAL PRIMARY KEY,
    display_order      BIGINT,
    title              TEXT,
    type               TEXT,
    m_mf_category_l_id INTEGER
        CONSTRAINT fk_m_mf_categ_m_budget_olvct0qexj
        REFERENCES m_mf_category_l,
    set_amount         NUMERIC,
    set_amount_credit  NUMERIC
);

CREATE INDEX fk_m_mf_categ_m_budget_jqugsdhpem
    ON m_budget (m_mf_category_l_id);

CREATE INDEX m_budget_order_idx
    ON m_budget (display_order);