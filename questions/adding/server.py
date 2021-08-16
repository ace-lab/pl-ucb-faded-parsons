def generate(data):

    # Define the variables here
    names_for_user = []
    names_from_user = [
        {"name": "add", "description": "python function that returns sum of 2 numbers", "type": "python function"}
    ]

    data["params"]["names_for_user"] = names_for_user
    data["params"]["names_from_user"] = names_from_user

    return data