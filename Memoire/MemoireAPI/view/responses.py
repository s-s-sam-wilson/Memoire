import base64
import os
import uuid
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework import status
from ..serializers import ResponseSerializer, ResponseAnswerSerializer
from base.models import Responses, Url_slambook, Questions, Response_answer, Question_Options, Slambooks
from django.conf import settings
from rest_framework.views import Response

# Create FileSystemStorage instance with media location
fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)




@api_view(['GET', 'POST'])
def response_list_create(request, slamid):

    try:
        slambook = Slambooks.objects.get(slamid=slamid, userid=request.session['userid'])
    except Slambooks.DoesNotExist:
        return Response({"error": "Slambook does not exist"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        responses = Responses.objects.filter(slamid=slamid)
        serializer = ResponseSerializer(responses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = ResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def submit_slambook_response(request, urlid):
    try:
        url_entry = Url_slambook.objects.get(urlid=urlid)
        slambook = url_entry.slamid
        answers_data = request.data.get('answers', {})
        response = Responses.objects.create(slamid=slambook)

        for question_id, answer_value in answers_data.items():
            try:
                question = Questions.objects.get(
                    questionid=question_id,
                    slamid=slambook
                )

                answer_data = {
                    'responseid': response,
                    'questionid': question
                }

                if question.type in ['MCQ', 'MSQ']:
                    answer = Response_answer.objects.create(**answer_data)
                    # Expect answer_value to be a list of option IDs
                    option_ids = answer_value if isinstance(answer_value, list) else [answer_value]
                    options = Question_Options.objects.filter(
                        questionid=question,
                        optionid__in=option_ids
                    )
                    if len(options) != len(option_ids):
                        raise Question_Options.DoesNotExist("Invalid option ID")
                    answer.answer_option.set(options)

                elif question.type in ['Text_One', 'Text_multi']:
                    Response_answer.objects.create(
                        **answer_data,
                        answer_text=answer_value
                    )

                elif question.type == 'IMAGE':
                    cleanpath = str(answer_value).replace('/media/', '').replace('/media', '')
                    Response_answer.objects.create(
                        **answer_data,
                        answer_image=cleanpath
                    )

                elif question.type == 'DATE':
                    Response_answer.objects.create(
                        **answer_data,
                        answer_text=answer_value
                    )

                elif question.type == 'Bottle':
                    Response_answer.objects.create(
                        **answer_data,
                        bottle_value=int(answer_value)
                    )

                elif question.type == 'Sign':
                    cleanpath = str(answer_value).replace('/media/', '').replace('/media', '')
                    Response_answer.objects.create(
                        **answer_data,
                        answer_image=cleanpath
                    )

            except (Questions.DoesNotExist, Question_Options.DoesNotExist) as e:
                return Response(
                    {"error": f"Invalid question or option: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"message": "Responses submitted successfully"},
            status=status.HTTP_201_CREATED
        )

    except Url_slambook.DoesNotExist:
        return Response(
            {"error": "Invalid slambook URL"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def upload_image(request):
    try:
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']
        if not file_obj.content_type.startswith('image/'):
            return Response({"error": "Only image files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 5 * 1024 * 1024
        if file_obj.size > max_size:
            return Response({"error": "File size exceeds 5MB limit"}, status=status.HTTP_400_BAD_REQUEST)

        filename, ext = os.path.splitext(file_obj.name)
        unique_filename = f"{filename}_{uuid.uuid4().hex}{ext}"

        # Save to /media/filename
        saved_filename = fs.save(unique_filename, file_obj)

        # Return only the filename (no /media/)
        return Response({"fileUrl": saved_filename}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"Upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def response_answers(request, responseid):
    try:
        response = Responses.objects.get(responseid=responseid)
        answers = Response_answer.objects.filter(responseid=response).prefetch_related('answer_option')
        serializer = ResponseAnswerSerializer(answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Responses.DoesNotExist:
        return Response({"error": "Response not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_image(request, filename):
    try:
        # Fetch from /media/filename
        file_path = fs.path(filename)

        if not os.path.exists(file_path):
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        with open(file_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
            content_type = "image/jpeg"
            if filename.endswith(".png"):
                content_type = "image/png"
            elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif filename.endswith(".gif"):
                content_type = "image/gif"

            return Response(
                {"imageData": f"data:{content_type};base64,{image_data}"},
                status=status.HTTP_200_OK
            )
    except Exception as e:
        return Response({"error": f"Failed to fetch image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)