-- MF大項目マスタ
DROP TABLE IF EXISTS m_mf_category_l;
CREATE TABLE m_mf_category_l
(
    id            SERIAL PRIMARY KEY,
    display_order BIGINT,
    title         TEXT
);

CREATE INDEX m_mf_category_l_order_idx
    ON m_mf_category_l (display_order);