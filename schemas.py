def DictSerializer(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=="_id"} ,**{i:a[i] for i in a if i!="_id"}}

def ListSerializer(entity) -> list:
    return [DictSerializer(a) for a in entity]

