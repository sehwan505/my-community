from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, permissions
import json
from .models import Post,Comment
from login.models import Profile
from .serializers import PostSerializer, CommentSerializer, PostListSerializer
from login.views import get_profile
from .pagination import ResultsSetPagination

class ListPost(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    #queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostListSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self, **kwargs):
        pk = self.kwargs.get('pk')
        queryset = Post.objects.filter(section=pk).order_by('-created_at')
        return queryset

class DetailPost(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

class DetailComment(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CommentSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self, **kwargs):
        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        queryset = Comment.objects.filter(post=post).order_by('parent_comment_id')
        return queryset

@api_view(["POST"])
def DeleteComment(request,pk):
    comment = Comment.objects.get(pk=pk)
    comment.delete()
    serializer = CommentSerializer()

    return JsonResponse({'comments': serializer.data}, safe=False, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def DeletePost(request,pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    serializer = PostSerializer()

    return JsonResponse({'posts': serializer.data}, safe=False, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
@csrf_exempt
def AddPost(request):
    payload = json.loads(request.body)
    print(payload)
    try:
        post = Post.objects.create(
            title=payload["title"],
            content=payload["content"],
            writer_id=payload["writer_id"],
            writer_name=payload["writer_name"],
			section=payload["section"],
        )
        profile = Profile.objects.get(user_pk = payload["writer_id"])
        profile.user_postlist.add(post)
        serializer = PostSerializer(post)
        return JsonResponse({'posts': serializer.data}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
@csrf_exempt
def AddComment(request,pk):
    payload = json.loads(request.body)
    post = Post.objects.get(pk=pk)
    try:
        if payload["depth"] == 0:
            comment = Comment.objects.create(
                post = post,
                content=payload["content"],
                writer_id=payload["writer_id"],
                writer_name=payload["writer_name"],
                depth=payload["depth"],
            )
            comment.parent_comment_id = comment.comment_id
            comment.save()
        else:
            comment = Comment.objects.create(
                post = post,
                content=payload["content"],
                writer_id=payload["writer_id"],
                writer_name=payload["writer_name"],
                parent_comment_id=payload["parent_comment_id"],
                depth=payload["depth"]
            )
        profile = Profile.objects.get(user_pk = payload["writer_id"])
        profile.user_postlist.add(post)
        serializer = CommentSerializer(comment)
        return JsonResponse({'comments': serializer.data}, safe=False, status=status.HTTP_201_CREATED)

    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def post_like(request, post_id):
    try:
        if (post := get_object_or_404(Post, id = post_id)):
            return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        profile = get_profile(request.META['HTTP_AUTHORIZATION'][4:])
        check_like_post = profile.user_post_like.filter(id=post_id)
        if check_like_post.exists():
            profile.user_post_like.remove(post)
            post.like_num -= 1
            post.save()
        else:
            profile.user_post_like.add(post)
            post.like_num += 1
            post.save()
        return JsonResponse({},status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def comment_like(request, comment_id):
    try:
        comment = get_object_or_404(Comment, comment_id = comment_id)
        profile = get_profile(request.META['HTTP_AUTHORIZATION'][4:]) #앞의 JWT를 뗴고 token을 보냄
        check_like_post = profile.user_comment_like.filter(comment_id = comment_id)
        if check_like_post.exists():
            profile.user_comment_like.remove(comment)
            comment.like_num -= 1
            comment.save()
        else:
            profile.user_comment_like.add(comment)
            comment.like_num += 1
            comment.save()
        return JsonResponse({},status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
@csrf_exempt
def upload_image(request):
    print(request.body ,1)
    return JsonResponse({'ok':1},status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes((AllowAny,))
def search_query(request):
    posts = None
    query = None
    if request.GET['query']:
        query = request.GET.get('query')
        posts = Post.objects.all().filter(Q(title__contains=query) | Q(content__contains=query))
        #Q(one_line__contains=query) | Q(content_list__contains=query))
        serializer = PostSerializer(posts, many=True)
        return JsonResponse({'posts': serializer.data}, safe=False, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error': 'Something terrible went wrong'}, safe=False, status=status.HTTP_200_OK)
