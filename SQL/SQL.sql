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

SELECT * FROM USERS;
SELECT * FROM USER_DETAILS;

DROP TABLE USERS;
DROP TABLE USER_DETAILS;