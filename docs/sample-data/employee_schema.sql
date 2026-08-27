-- Oracle DDL: Employee Management Schema
-- Contains classic Oracle-specific constructs that need migration attention

CREATE SEQUENCE emp_seq START WITH 1000 INCREMENT BY 1 NOCACHE NOCYCLE;

CREATE TABLE employees (
    emp_id       NUMBER(10) PRIMARY KEY,
    first_name   VARCHAR2(50) NOT NULL,
    last_name    VARCHAR2(50) NOT NULL,
    hire_date    DATE DEFAULT SYSDATE,
    salary       NUMBER(10,2),
    manager_id   NUMBER(10),
    dept_id      NUMBER(5)
);

-- Oracle uses a TRIGGER + SEQUENCE to simulate auto-increment,
-- since Oracle (pre-12c) has no native IDENTITY column.
CREATE OR REPLACE TRIGGER trg_emp_id
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
    IF :NEW.emp_id IS NULL THEN
        SELECT emp_seq.NEXTVAL INTO :NEW.emp_id FROM DUAL;
    END IF;
END;
/

-- ROWNUM-based pagination: Oracle-specific, does not translate directly
-- to PostgreSQL (which uses LIMIT/OFFSET instead).
CREATE OR REPLACE VIEW top_10_earners AS
SELECT * FROM (
    SELECT emp_id, first_name, last_name, salary
    FROM employees
    ORDER BY salary DESC
)
WHERE ROWNUM <= 10;