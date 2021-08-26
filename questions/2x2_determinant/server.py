def generate(data):

    # Define the variables here
    names_for_user = []
    names_from_user = [
        {"name": "det", "description": "determinant for a 2x2 matrix", "type": "python function"}
    ]

    data["params"]["names_for_user"] = names_for_user
    data["params"]["names_from_user"] = names_from_user

    return data