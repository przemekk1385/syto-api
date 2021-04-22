def is_owner(request, view, view_action: str) -> bool:
    obj = view.get_object()

    return request.user == obj.user
