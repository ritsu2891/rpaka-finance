-- 口座マスタ
DROP TABLE IF EXISTS m_account;
CREATE TABLE m_account
(
    id                SERIAL PRIMARY KEY,
    display_order     BIGINT,
    title             TEXT,
    m_account_type_id INTEGER
        CONSTRAINT fk_m_account__m_account_kt7078u8yd
        REFERENCES m_account_type
);

CREATE INDEX fk_m_account__m_account_a558wf8iki
    ON m_account (m_account_type_id);

CREATE INDEX m_account_order_idx
    ON m_account (display_order);