import hashlib

def get_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# print("Yield model checksum:", get_checksum("models/crop_yield_model.pkl"))
# print("Recommendation model checksum:", get_checksum("models/crop_recommendation_model.pkl"))