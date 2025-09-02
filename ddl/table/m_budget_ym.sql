-- 予算年月マスタ
DROP TABLE IF EXISTS m_budget_ym;
CREATE TABLE m_budget_ym
(
    id            SERIAL PRIMARY KEY,
    display_order BIGINT,
    title         TEXT,
    year          BIGINT,
    month         BIGINT,
    from_date     DATE,
    to_date       DATE
);

CREATE INDEX m_budget_ym_order_idx
    ON m_budget_ym (display_order);