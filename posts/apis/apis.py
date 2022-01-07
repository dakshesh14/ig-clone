from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny


from posts.models import (
    Post,
    PostComment,
)

from .serializers import (
    PostCommentSerializer,
)


class PostCommentAPI(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        post_qs = get_object_or_404(Post, pk=pk)
        qs = PostComment.parent_objects.filter(post=post_qs).all()
        return qs

    def post(self, request, pk=None, format=None, *args, **kwargs):
        post_qs = get_object_or_404(Post, pk=pk)

        serializer = PostCommentSerializer(data=request.data)

        if serializer.is_valid():
            content = request.data.get("content")
            parent = request.data.get("parent_id")

            if parent:
                parent_qs = get_object_or_404(PostComment, pk=parent)
            else:
                parent_qs = None

            instance = serializer.save(
                content=content,
                parent=parent_qs,
                post=post_qs,
            )
            instance.likes.add(self.request.user)

            return Response(data=serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)