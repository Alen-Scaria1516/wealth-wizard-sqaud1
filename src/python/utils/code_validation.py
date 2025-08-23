from oracledb import NUMBER
def code_validation(email_id, inputToken, connection):
    cursor = connection.cursor()
    num_status = cursor.callfunc("CodeValidation", NUMBER ,[email_id, inputToken])
    status = False
    if num_status == 1: 
        status =  True
    elif num_status == 0:
        status = False
    else:
        status = False
    
    cursor.close()
    return status
    