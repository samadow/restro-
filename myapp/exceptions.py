from rest_framework.views import exception_handler


def first_message(data):
    if isinstance(data, list) and data:
        return first_message(data[0])

    if isinstance(data, dict) and data:
        if "error" in data:
            return first_message(data["error"])
        if "detail" in data:
            return first_message(data["detail"])

        key, value = next(iter(data.items()))
        return f"{key}: {first_message(value)}"

    return str(data)


def error_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    response.data = {
        "error": first_message(response.data),
        "details": response.data,
        "status_code": response.status_code
    }

    return response
