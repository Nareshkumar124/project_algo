def userEntity(user):
    return {
        "id":str(user["_id"]),
        "username":user["username"],
        "password":user["password"],
        "email":user["email"]
    }
    