from django.contrib.auth import get_user_model

UserModel = get_user_model()


def get_client(document):
    try:
        user = UserModel.objects.get(document=document)
        return user
    except UserModel.DoesNotExist:
        return None
