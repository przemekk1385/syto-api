def is_owner(request, view, action: str) -> bool:
    obj = view.get_object()

    return request.user == obj.user
