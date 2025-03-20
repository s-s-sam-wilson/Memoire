from rest_framework.views import Response
from rest_framework.decorators import api_view
from ..serializers import QuestionSerializer, QuestionOptionSerializer
from base.models import Questions, Question_Options, Slambooks
from rest_framework import status

# views/questions.py
from rest_framework.views import Response
from rest_framework.decorators import api_view
from rest_framework import status
from ..serializers import QuestionSerializer
from base.models import Questions

@api_view(['POST', 'GET', 'PUT'])
def question_view(request, slamid):
    if 'userid' not in request.session:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        slambook = Slambooks.objects.get(slamid=slamid, userid=request.session['userid'])
    except Slambooks.DoesNotExist:
        return Response({"error": "Slambook does not exist"}, status=status.HTTP_404_NOT_FOUND)



    # Create question
    if request.method == 'POST':
        data = request.data.copy()
        data['slamid'] = slamid
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            question = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # List all questions in a slambook
    elif request.method == 'GET':

        questions = Questions.objects.filter(slamid=slamid)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update question sequence
    elif request.method == 'PUT':
        try:
            # Expecting a list of objects with questionid and sequence
            for item in request.data:
                question = Questions.objects.get(questionid=item['questionid'], slamid=slamid)
                question.sequence = item['sequence']
                question.save()
            return Response({"message": "Question order updated successfully"}, status=status.HTTP_200_OK)
        except Questions.DoesNotExist:
            return Response({"error": "One or more questions not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PUT'])
def question_single_view(request, slamid, questionid):
    if 'userid' not in request.session:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        slambook = Slambooks.objects.get(slamid=slamid, userid=request.session['userid'])
    except Slambooks.DoesNotExist:
        return Response({"error": "Slambook does not exist"}, status=status.HTTP_404_NOT_FOUND)

    try:
        question = Questions.objects.get(questionid=questionid, slamid=slamid)
    except Exception as e:
        return Response({"error": "Given Question not available"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        question.delete()
        return Response({"message": "Question deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def question_option_view(request, slamid, questionid):
    if 'userid' not in request.session:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        slambook = Slambooks.objects.get(slamid=slamid, userid=request.session['userid'])
    except Slambooks.DoesNotExist:
        return Response({"error": "Slambook does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Create question option
    if request.method == 'POST':
        data = request.data.copy()
        data['questionid'] = questionid
        serializer = QuestionOptionSerializer(data=data)
        if serializer.is_valid():
            option = serializer.save()  # Save and get the created instance
            # Return the serialized data of the created option
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # List all options for a question
    elif request.method == 'GET':
        question_options = Question_Options.objects.filter(questionid=questionid).order_by('created')
        serializer = QuestionOptionSerializer(question_options, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'DELETE', 'PUT'])
def question_option_single_view(request, slamid, questionid, optionid):
    if 'userid' not in request.session:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        slambook = Slambooks.objects.get(slamid=slamid, userid=request.session['userid'])
    except Slambooks.DoesNotExist:
        return Response({"error": "Slambook does not exist"}, status=status.HTTP_404_NOT_FOUND)

    try:
        question_option = Question_Options.objects.get(questionid=questionid, optionid=optionid)
    except Exception as e:
        return Response({"error": "Given option not available"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionOptionSerializer(question_option)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        question_option.delete()
        return Response({"message": "Question option deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = QuestionOptionSerializer(question_option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)