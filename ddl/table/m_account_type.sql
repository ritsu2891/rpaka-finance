-- 口座種別マスタ
DROP TABLE IF EXISTS m_account_type;
CREATE TABLE m_account_type
(
    id            SERIAL PRIMARY KEY,
    display_order BIGINT,
    title         TEXT
);

CREATE INDEX m_account_type_order_idx
    ON m_account_type (display_order);