-- M2M：m_budget - m_mf_category_m
DROP TABLE IF EXISTS _nc_m2m_m_mf_category_m_m_budget;
CREATE TABLE _nc_m2m_m_mf_category_m_m_budget
(
    m_budget_id        INTEGER NOT NULL
        CONSTRAINT fk_m_mf_categ_m_budget_vhn6in9ln8
        REFERENCES m_budget,
    m_mf_category_m_id INTEGER NOT NULL
        CONSTRAINT fk_m_mf_categ_m_budget_jwt1xdq_g8
        REFERENCES m_mf_category_m,
    PRIMARY KEY (m_budget_id, m_mf_category_m_id)
);

CREATE INDEX fk_m_mf_categ_m_budget_dmrolzxh9w
    ON _nc_m2m_m_mf_category_m_m_budget (m_budget_id);

CREATE INDEX fk_m_mf_categ_m_budget_u8by5t82zu
    ON _nc_m2m_m_mf_category_m_m_budget (m_mf_category_m_id);