from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Member(models.Model):
    """
    Custom user model for the application.
    Not using Django's built-in User model as per requirements.
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'members'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        return check_password(raw_password, self.password_hash)

    @property
    def is_authenticated(self):
        """Always return True for authenticated members."""
        return True

    @property
    def is_anonymous(self):
        """Always return False for members."""
        return False

    def has_perm(self, perm, obj=None):
        """For DRF permission compatibility."""
        return True

    def has_module_perms(self, app_label):
        """For DRF permission compatibility."""
        return True


class Message(models.Model):
    """
    Message model for chat messages.
    """
    author = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"Message by {self.author.username} at {self.created_at}"
