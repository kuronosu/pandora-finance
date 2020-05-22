import uuid


def generate_code(model_name):
    class_code = str(hex(int(sum([ord(c) for c in model_name]))))[2:]
    str_uuid = str(uuid.uuid4())
    str_uuid = class_code + \
        str_uuid[len(class_code) if len(class_code) < 8 else 8:]
    return uuid.UUID(str_uuid)
