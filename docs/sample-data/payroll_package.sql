-- Oracle PL/SQL Package: Payroll Processing
-- PACKAGE/PACKAGE BODY has no direct PostgreSQL equivalent —
-- must be converted to a set of individual functions/procedures
-- inside a schema, since PostgreSQL has no package construct.

CREATE OR REPLACE PACKAGE payroll_pkg AS
    FUNCTION calculate_bonus(p_emp_id NUMBER) RETURN NUMBER;
    PROCEDURE apply_annual_raise(p_dept_id NUMBER, p_percentage NUMBER);
END payroll_pkg;
/

CREATE OR REPLACE PACKAGE BODY payroll_pkg AS

    FUNCTION calculate_bonus(p_emp_id NUMBER) RETURN NUMBER IS
        v_salary NUMBER;
    BEGIN
        SELECT salary INTO v_salary FROM employees WHERE emp_id = p_emp_id;
        RETURN v_salary * 0.10;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RETURN 0;
    END calculate_bonus;

    PROCEDURE apply_annual_raise(p_dept_id NUMBER, p_percentage NUMBER) IS
    BEGIN
        UPDATE employees
        SET salary = salary * (1 + p_percentage/100)
        WHERE dept_id = p_dept_id;
        COMMIT;
    END apply_annual_raise;

END payroll_pkg;
/