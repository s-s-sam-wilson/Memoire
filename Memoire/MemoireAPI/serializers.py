from rest_framework import serializers
from base.models import User, Slambooks, Questions, Question_Options, Response_answer, Responses, Url_slambook
from django.contrib.auth.hashers import make_password, check_password
from PIL import Image
import numpy as np
import cv2
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def create(self, validated_data):
        user = User(
            name = validated_data['name'],
            email = validated_data['email']
        )
        user.set_password(raw_password=validated_data['password'])
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SlambookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slambooks
        fields = ['slamid', 'userid', 'slamtitle', 'created', 'modified']
        read_only_fields = ['slamid', 'created', 'modified']
        extra_kwargs = {'userid': {'write_only': True}}


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['questionid', 'slamid','questiontext', 'type', 'max_selection', 'is_required', 'created', 'modified', 'sequence']

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question_Options
        fields = ['optionid', 'questionid', 'optiontext', 'created', 'modified']


def remove_background(image):
    image = Image.open(image).convert("RGBA")
    np_image = np.array(image)

    # Assuming white background, make pixels with high intensity transparent
    r, g, b, a = np.rollaxis(np_image, axis=-1)
    mask = (r > 200) & (g > 200) & (b > 200)
    np_image[mask] = (255, 255, 255, 0)

    # Convert back to Image and save to BytesIO
    image_with_transparency = Image.fromarray(np_image)
    buffer = io.BytesIO()
    image_with_transparency.save(buffer, format="PNG")
    buffer.seek(0)

    return InMemoryUploadedFile(
        buffer,
        field_name=None,
        name="processed_signature.png",
        content_type="image/png",
        size=buffer.getbuffer().nbytes,
        charset=None,
    )

class ResponseAnswerSerializer(serializers.ModelSerializer):
    answer_option = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Response_answer
        fields = ['answerid', 'responseid', 'questionid', 'answer_text',
                 'answer_image', 'bottle_value', 'answer_option',
                 'created', 'modified']

    def validate(self, data):
        if data.get('questionid').type == 'Sign' and data.get('answer_text'):
            data['answer_text'] = remove_background(data['answer_text'])
        return data

class ResponseSerializer(serializers.ModelSerializer):
    response_answers = ResponseAnswerSerializer(many=True, read_only=True)  # Changed to read_only

    class Meta:
        model = Responses
        fields = ['responseid', 'slamid', 'created', 'modified', 'response_answers']

    def create(self, validated_data):
        response_answers_data = validated_data.pop('response_answers', [])
        response = Responses.objects.create(**validated_data)
        for answer_data in response_answers_data:
            answer_options = answer_data.pop('answer_option', [])
            response_answer = Response_answer.objects.create(responseid=response, **answer_data)
            response_answer.answer_option.set(answer_options)
        return response

class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url_slambook
        fields = ['urlid', 'slamid', 'created']


