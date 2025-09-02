-- MF中項目マスタ
DROP TABLE IF EXISTS m_mf_category_m;
CREATE TABLE m_mf_category_m
(
    id                 SERIAL PRIMARY KEY,
    display_order      BIGINT,
    title              TEXT,
    m_mf_category_l_id INTEGER
        CONSTRAINT fk_m_mf_categ_m_mf_categ_f0sueozytp
        REFERENCES m_mf_category_l
);

CREATE INDEX fk_m_mf_categ_m_mf_categ_u26yh8_n37
    ON m_mf_category_m (m_mf_category_l_id);

CREATE INDEX m_mf_category_m_order_idx
    ON m_mf_category_m (display_order);