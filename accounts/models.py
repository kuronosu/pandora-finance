
import uuid
from django.db.models.constraints import CheckConstraint, Q
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from common.util import generate_code

from .managers import UserManager
from .validators import DNIValidator, PhoneValidator, NameValidator


def generate_code_user():
    return generate_code('User')


class User(AbstractBaseUser, PermissionsMixin):
    types = (1, 2)
    USER_TYPE_CHOICES = (
        (types[0], 'empleado'),
        (types[1], 'cliente'),
    )

    id = models.UUIDField('Código', primary_key=True,
                          default=generate_code_user, editable=False)
    document = models.CharField(
        'Cédula', validators=[DNIValidator()], max_length=10, unique=True)
    first_name = models.CharField(
        'Nombres', validators=[NameValidator()], max_length=30)
    last_name = models.CharField('Apellidos', validators=[
                                 NameValidator()], max_length=150)
    phone_number = models.CharField(
        validators=[PhoneValidator()], max_length=17)
    email = models.EmailField('Correo electronico')
    address1 = models.CharField('Dirección 1', max_length=1024)
    address2 = models.CharField(
        'Dirección 2', max_length=1024, blank=True, null=True)
    birthdate = models.DateField('Fecha de nacimiento')
    user_type = models.PositiveSmallIntegerField('Tipo de usuario', choices=USER_TYPE_CHOICES)
    can_approve = models.BooleanField('Puede aprobar', default=False)
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designa si este usuario debe ser tratado como activo.\nSeleccione esto en lugar de eliminar cuentas.',
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'document'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name',
                       'phone_number', 'address1', 'birthdate', 'user_type']

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        swappable = 'AUTH_USER_MODEL'
        constraints = [
            CheckConstraint(check=(Q(can_authorize=True) & Q(user_type=1)) | (
                Q(can_authorize=False) & Q(user_type__in=(1, 2))), name='can_authorize_only_employee'),
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_client(self):
        return self.user_type == self.types[1]

    @property
    def is_employee(self):
        return self.user_type == self.types[0]

    @property
    def client_type(self):
        return User.types[1]

    @property
    def employee_type(self):
        return User.types[0]
