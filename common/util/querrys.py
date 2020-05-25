from django.contrib.auth import get_user_model

UserModel = get_user_model()


def verify_exist(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def get_client(document=None, **kwargs):
    if document:
        kwargs.update({'document': document})
    if not bool(kwargs):
        return None
    try:
        user = UserModel.objects.get(**kwargs)
        return user
    except UserModel.DoesNotExist:
        return None
