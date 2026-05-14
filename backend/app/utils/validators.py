def validate_no_space(value: str):
    if " " in value:
        raise ValueError("Không được có khoảng trắng")
    return value