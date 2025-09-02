-- 予定入出金
DROP TABLE IF EXISTS t_planned_cf;
CREATE TABLE t_planned_cf
(
    id                     SERIAL PRIMARY KEY,
    title                  TEXT,
    date                   DATE,
    amount                 NUMERIC,
    m_mf_category_l_id     INTEGER
        CONSTRAINT fk_m_mf_categ_t_planned__pb6k4hlaw0
        REFERENCES m_mf_category_l,
    m_mf_category_m_id     INTEGER
        CONSTRAINT fk_m_mf_categ_t_planned__pl91hlqd4i
        REFERENCES m_mf_category_m,
    m_account_id           INTEGER
        CONSTRAINT fk_m_account_t_planned__uvjl3legpy
        REFERENCES m_account,
    m_repeat_planned_cf_id INTEGER
        CONSTRAINT fk_m_repeat_p_t_planned__5asglx_pdr
        REFERENCES m_repeat_planned_cf
);

CREATE INDEX fk_m_mf_categ_t_planned__r3s2gg7qfj
    ON t_planned_cf (m_mf_category_l_id);

CREATE INDEX fk_m_mf_categ_t_planned__n0j8_9trpw
    ON t_planned_cf (m_mf_category_m_id);

CREATE INDEX fk_m_account_t_planned__ihe7n3hkjb
    ON t_planned_cf (m_account_id);

CREATE INDEX fk_m_repeat_p_t_planned__x7st56s8j7
    ON t_planned_cf (m_repeat_planned_cf_id);