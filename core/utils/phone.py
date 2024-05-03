def format_phone_number(
        *,
        phone_number,
):
    if '+' in str(phone_number) and phone_number[0] == '+':
        phone_number = phone_number[1:]

    return phone_number
