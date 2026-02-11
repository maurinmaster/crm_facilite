from django.db import models


class Client(models.Model):
    id = models.TextField(primary_key=True)
    org_id = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    cnpj = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'clients'
        managed = False


class ClientContact(models.Model):
    id = models.TextField(primary_key=True)
    client_id = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    role = models.TextField(null=True, blank=True)
    department = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    instagram = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'client_contacts'
        managed = False


class ClientCredentialSimple(models.Model):
    id = models.TextField(primary_key=True)
    client_id = models.TextField(null=True, blank=True)
    site = models.TextField(null=True, blank=True)
    usuario = models.TextField(null=True, blank=True)
    senha = models.TextField(null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    obs = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'client_credentials_simple'
        managed = False


class ClientLink(models.Model):
    id = models.TextField(primary_key=True)
    client_id = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'client_links'
        managed = False


class User(models.Model):
    id = models.UUIDField(primary_key=True)
    email = models.TextField(unique=True)
    name = models.TextField()
    password_hash = models.TextField()
    is_admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'users'
        managed = False


class Session(models.Model):
    id = models.UUIDField(primary_key=True)
    user_id = models.UUIDField()
    token = models.TextField(unique=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'sessions'
        managed = False
