-- 定期予定入出金マスタ
DROP TABLE IF EXISTS m_repeat_planned_cf;
CREATE TABLE m_repeat_planned_cf
(
    id                 INTEGER
        DEFAULT nextval('t_repeat_planned_id_seq'::regclass)
        NOT NULL
        CONSTRAINT t_repeat_planned_pkey PRIMARY KEY,
    display_order      BIGINT,
    title              TEXT,
    interval_type      TEXT,
    month              BIGINT,
    day                BIGINT,
    amount             NUMERIC,
    m_mf_category_l_id INTEGER
        CONSTRAINT fk_m_mf_categ_m_repeat_p_fyr353f9a1
        REFERENCES m_mf_category_l,
    m_mf_category_m_id INTEGER
        CONSTRAINT fk_m_mf_categ_m_repeat_p_fdjiddkbqv
        REFERENCES m_mf_category_m,
    m_account_id       INTEGER
        CONSTRAINT fk_m_account_m_repeat_p_6ocyucqux2
        REFERENCES m_account,
    enable             BOOLEAN DEFAULT true,
    mf_title_pattern   TEXT
);

CREATE INDEX fk_m_mf_categ_m_repeat_p_mchqamqmks
    ON m_repeat_planned_cf (m_mf_category_l_id);

CREATE INDEX fk_m_mf_categ_m_repeat_p_g7kvxxl2ws
    ON m_repeat_planned_cf (m_mf_category_m_id);

CREATE INDEX fk_m_account_m_repeat_p_rgvc2svnp2
    ON m_repeat_planned_cf (m_account_id);

CREATE INDEX t_repeat_planned_order_idx
    ON m_repeat_planned_cf (display_order);