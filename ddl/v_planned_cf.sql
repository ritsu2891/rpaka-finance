DROP VIEW IF EXISTS v_planned_cf;
CREATE VIEW v_planned_cf AS
SELECT
    t_p.id, t_p.title, t_p.date, t_p.amount,
    CASE WHEN t_c.id IS NULL THEN '' ELSE '消込済' END AS is_done
FROM t_planned_cf t_p
LEFT JOIN t_mf_cf t_c ON t_p.id = t_c.t_planned_cf_id
ORDER BY t_p.date, t_p.id;