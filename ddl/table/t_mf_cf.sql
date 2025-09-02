-- MF入出金
DROP TABLE IF EXISTS t_mf_cf;
CREATE TABLE t_mf_cf
(
    id                 SERIAL PRIMARY KEY,
    created_at         TIMESTAMP,
    updated_at         TIMESTAMP,
    title              TEXT,
    calc_target        BOOLEAN DEFAULT FALSE,
    date               DATE,
    amount             NUMERIC,
    m_account_id       INTEGER
        CONSTRAINT fk_m_account_t_mf_cf_7pl19csp7d
        REFERENCES m_account,
    m_mf_category_l_id INTEGER
        CONSTRAINT fk_m_mf_categ_t_mf_cf_gfauv6umsj
        REFERENCES m_mf_category_l,
    m_mf_category_m_id INTEGER
        CONSTRAINT fk_m_mf_categ_t_mf_cf_ss55kuzqda
        REFERENCES m_mf_category_m,
    memo               TEXT,
    transfer           BOOLEAN DEFAULT FALSE,
    mf_id              TEXT,
    t_planned_cf_id    INTEGER
        CONSTRAINT fk_t_planned__t_mf_cf_11wr55bgik
        REFERENCES t_planned_cf,
    t_mf_cf_id         INTEGER
        CONSTRAINT fk_t_mf_cf_t_mf_cf_2693m2i6o2
        REFERENCES t_mf_cf
);

CREATE INDEX fk_m_account_t_mf_cf_saivomvq6v
    ON t_mf_cf (m_account_id);

CREATE INDEX fk_m_mf_categ_t_mf_cf_w0oafs_lcj
    ON t_mf_cf (m_mf_category_l_id);

CREATE INDEX fk_m_mf_categ_t_mf_cf_j0bufnkyir
    ON t_mf_cf (m_mf_category_m_id);

CREATE INDEX fk_t_planned__t_mf_cf_1qsos8wqrk
    ON t_mf_cf (t_planned_cf_id);

CREATE INDEX fk_t_mf_cf_t_mf_cf_4zavujmqqi
    ON t_mf_cf (t_mf_cf_id);