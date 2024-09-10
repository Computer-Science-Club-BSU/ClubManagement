CREATE OR REPLACE VIEW current_term AS
    SELECT t.seq FROM terms t WHERE
CURRENT_TIMESTAMP BETWEEN t.start_date AND t.end_date

