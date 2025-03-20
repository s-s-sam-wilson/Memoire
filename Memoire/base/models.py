import uuid
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator


class User(models.Model):
    # Replace AutoField with UUIDField
    userid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=200, null=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()], null=False)
    password = models.CharField(max_length=128, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Slambooks(models.Model):
    # Replace AutoField with UUIDField
    slamid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    slamtitle = models.CharField(max_length=200, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Questions(models.Model):
    class Question_type(models.TextChoices):
        MCQ = 'MCQ'
        MSQ = 'MSQ'
        Text_One = 'Text_One'
        Text_multi = 'Text_multi'
        Image = 'IMAGE'
        Date = 'DATE'
        Bottle = 'Bottle'
        Sign = 'Sign'

    # Replace AutoField with UUIDField
    questionid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    slamid = models.ForeignKey(Slambooks, on_delete=models.CASCADE, null=False)
    questiontext = models.CharField(max_length=1000, null=False)
    type = models.CharField(max_length=10, choices=Question_type, null=False)
    max_selection = models.IntegerField(default=0)
    is_required = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    sequence = models.IntegerField(default=0)  # New field for order

    class Meta:
        ordering = ['sequence']  # Default ordering by sequence (removed questionid)


class Question_Options(models.Model):
    # Replace AutoField with UUIDField
    optionid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    questionid = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE,
        null=False,
        related_name='options')
    optiontext = models.CharField(max_length=150, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Url_slambook(models.Model):
    # Already using UUIDField, no change needed
    urlid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    slamid = models.ForeignKey(Slambooks, on_delete=models.CASCADE, null=False)
    created = models.DateTimeField(auto_now_add=True)


class Responses(models.Model):
    # Replace AutoField with UUIDField
    responseid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    slamid = models.ForeignKey(Slambooks, on_delete=models.CASCADE, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Response_answer(models.Model):
    # Replace AutoField with UUIDField
    answerid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    responseid = models.ForeignKey(Responses, on_delete=models.CASCADE, null=False)
    questionid = models.ForeignKey(Questions, on_delete=models.CASCADE, null=False)
    answer_text = models.TextField(null=True, blank=True)  # For text/image/bottle answers
    answer_option = models.ManyToManyField(
        Question_Options, blank=True
    )
    answer_image = models.CharField(max_length=255, null=True, blank=True)
    bottle_value = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)