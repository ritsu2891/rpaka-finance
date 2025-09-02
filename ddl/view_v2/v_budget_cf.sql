DROP VIEW IF EXISTS v_budget_cf;
CREATE VIEW v_budget_cf AS
WITH
cfs AS (
    SELECT
        id, mf_id, date, title,
        amount,
        m_account_id, m_mf_category_l_id, m_mf_category_m_id
    FROM t_mf_cf
    WHERE calc_target = true AND t_mf_cf_id IS NULL
),
alt_cfs AS (
    SELECT
        org_cf.id, org_cf.mf_id, org_cf.date, org_cf.title,
        CASE
            WHEN 0 < org_cf.amount AND alt_cf.amount < 0 AND ABS(org_cf.amount) = ABS(alt_cf.amount) THEN alt_cf.amount
            ELSE org_cf.amount
        END AS amount,
        alt_cf.m_account_id, org_cf.m_mf_category_l_id,  org_cf.m_mf_category_m_id
    FROM t_mf_cf org_cf
    LEFT JOIN t_mf_cf AS alt_cf ON alt_cf.id = org_cf.t_mf_cf_id
    WHERE org_cf.t_mf_cf_id IS NOT NULL
)
SELECT * FROM cfs
UNION ALL
SELECT * FROM alt_cfs;