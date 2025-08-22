Create TABLE Users(    
    User_ID varchar(255) PRIMARY KEY,
    Email_ID VARCHAR2(100) NOT NULL UNIQUE,   
    Password VARCHAR2(255) NOT NULL,    
    last_modified TIMESTAMP,    
    is_Verified NUMBER(1) DEFAULT 0,    
    is_loggedIn NUMBER(1) DEFAULT 0,    
    token VARCHAR2(255)
);

Create table user_details(
    reg_id varchar2(255) primary key, 
    user_id varchar2(255) Unique Not null, 
    name varchar2(100) not null, 
    Age number, 
    constraint fk_user foreign key (user_id) references users(user_id)
);


-- Sequence 
CREATE SEQUENCE user_seq
START WITH 1
INCREMENT BY 1
NOCACHE;

CREATE SEQUENCE user_profile_seq
START WITH 1
INCREMENT BY 1
NOCACHE;

-- SELECT * FROM USERS;
-- SELECT * FROM USER_DETAILS;

-- DROP TABLE USERS;
-- DROP TABLE USER_DETAILS;

Create or REPLACE FUNCTION CodeValidation(p_email_ID Users.Email_ID%TYPE , inputToken Users.token%TYPE)
RETURN NUMBER
IS
    dbToken Users.token%TYPE;
    timeGenerated Users.last_modified%TYPE;
    v_Status NUMBER;
BEGIN
    Select token, last_modified into dbToken, timeGenerated from users WHERE Email_ID = p_email_ID;
    if (dbToken = inputToken) And (SYSTIMESTAMP - timeGenerated < NUMTODSINTERVAL(5, 'MINUTE'))  THEN
        DBMS_OUTPUT.PUT_LINE('User Verified Successfully');
        UPDATE Users SET is_verified = 1, last_modified = SYSTIMESTAMP WHERE email_id = p_email_ID;
        COMMIT;
        v_Status := 1;
    ELSE
        DBMS_OUTPUT.PUT_LINE('Incorrect token or token expired, verify again.');
        v_Status := 0;
    END IF;
    RETURN v_Status;
End;

-- SET SERVEROUTPUT on;
-- DECLARE
--     p_email_ID Users.Email_ID%TYPE := 'anurag291003sahu@gmail.com';
--     v_status NUMBER;
--     inputToken Users.token%TYPE := 'b7228634-9679-4af5-b469-7d248a1835fa';
-- BEGIN
--     v_status := CODEVALIDATION(P_EMAIL_ID, inputToken);
--     DBMS_OUTPUT.PUT_LINE(v_status);
-- END;

--check existing email for registration
create or replace PROCEDURE check_user_email (
    p_email     IN  VARCHAR2,
    p_exists    OUT NUMBER
)
AS
BEGIN
    SELECT COUNT(*)
    INTO p_exists
    FROM Users
    WHERE LOWER(email_id) = LOWER(p_email);

END;

-- Stored procedure to logout user
CREATE OR REPLACE PROCEDURE logout_user_proc(p_user_id IN NUMBER)
IS
BEGIN
    UPDATE Users
    SET is_loggedIn = 0,
        token = NULL,
        last_modified = SYSTIMESTAMP
    WHERE User_ID = p_user_id;
    COMMIT;
END logout_user_proc;

-- Stored procedure to expire session
CREATE OR REPLACE PROCEDURE expire_session_proc(p_user_id IN NUMBER)
IS
BEGIN
    UPDATE Users
    SET is_loggedIn = 0,
        token = NULL,
        last_modified = SYSTIMESTAMP
    WHERE User_ID = p_user_id;
    COMMIT;
END expire_session_proc;