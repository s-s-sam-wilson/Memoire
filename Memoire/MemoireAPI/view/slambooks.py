from rest_framework.views import Response
from rest_framework.decorators import api_view
from ..serializers import SlambookSerializer, UrlSerializer, QuestionSerializer, QuestionOptionSerializer
from base.models import Slambooks, Url_slambook, Question_Options, Questions
from rest_framework import status
import uuid


@api_view(['POST', 'GET'])
def slambook_view(request):
    if 'userid' not in request.session:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    #create slambook
    if request.method=='POST':
        data = request.data.copy()
        data['userid'] = request.session['userid']
        serializer = SlambookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Slambook created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #list all slambooks
    elif request.method=='GET':
        slambooks = Slambooks.objects.filter(userid=request.session['userid'])
        serializer = SlambookSerializer(slambooks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE', 'PUT', 'GET'])
def slambook_single_view(request, slamid):
    if 'userid' not in request.session:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        slambook = Slambooks.objects.get(slamid=slamid, userid=request.session['userid'])

        #get single slambook by slamid
        if request.method == 'GET':
            serializer = SlambookSerializer(slambook)
            return Response(serializer.data, status=status.HTTP_200_OK)

        #delete slambook
        elif request.method == 'DELETE':
            slambook.delete()
            return Response({"message": "Slambook deleted Sucessfully"}, status=status.HTTP_204_NO_CONTENT)

        #update slambook
        elif request.method == 'PUT':
            data = request.data.copy()
            data['userid'] = request.session['userid']
            serializer = SlambookSerializer(slambook, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Slambooks.DoesNotExist:
        return Response({"error": "Slambook does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_url_slambook(request, slamid):
    try:
        slambook = Slambooks.objects.get(slamid=slamid)
        try:
            url_entry = Url_slambook.objects.get(slamid=slambook)
            serializer = UrlSerializer(url_entry)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Url_slambook.DoesNotExist:
            new_url_entry = Url_slambook.objects.create(
                urlid=uuid.uuid4(),
                slamid=slambook
            )
            serializer = UrlSerializer(new_url_entry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Slambooks.DoesNotExist:
        return Response(
            {"error": f"Slambook with id {slamid} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_slambook_by_url(request, urlid):
    try:
        # Get the URL entry and related slambook
        url_entry = Url_slambook.objects.get(urlid=urlid)
        slambook = url_entry.slamid

        # Serialize slambook basic info
        slambook_serializer = SlambookSerializer(slambook)

        # Get all questions for this slambook
        questions = Questions.objects.filter(slamid=slambook)
        question_serializer = QuestionSerializer(questions, many=True)

        # Prepare response data
        response_data = {
            'slambook': slambook_serializer.data,
            'questions': []
        }

        # For each question, include options if they exist
        for question in questions:
            question_data = QuestionSerializer(question).data

            # Check if question type supports options (MCQ or MSQ)
            if question.type in ['MCQ', 'MSQ']:
                options = Question_Options.objects.filter(questionid=question.questionid)
                option_serializer = QuestionOptionSerializer(options, many=True)
                question_data['options'] = option_serializer.data
            else:
                question_data['options'] = []

            response_data['questions'].append(question_data)

        return Response(response_data, status=status.HTTP_200_OK)

    except Url_slambook.DoesNotExist:
        return Response(
            {"error": f"Slambook with URL ID {urlid} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )