from json import JSONDecodeError
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import views, status
from vara_backend.settings import CONTENT_PAGE_SIZE, SMALL_PAGE_SIZE


from .models import Video, Tag, ImageSlide, Image, VideoLike, ImageSlideLike, Playlist, Post, PostComment
from .serializers import VideoSerializer, VideoPostSerializer, VideoPutSerializer, TagSerializer \
    , ImageSlideSerializer, ImageSlidePostSerializer, ImageSlidePutSerializer, ImageSerializer \
    , ImagePostSerializer, ImageSlideDetailSerializer, ImageSlideLikeSerializer, VideoLikeSerializer \
    , ImageSlideCommentSerializer, VideoCommentSerializer, VideoCommentPostSerializer \
    , ImageSlideCommentPostSerializer, VideoCommentParamSerializer, ImageSlideCommentParamSerializer \
    , ImageSlideCommentPutSerializer, VideoCommentPutSerializer, PlaylistSerializer, PlaylistNameSerializer \
    , PlaylistDetailSerializer, UserIDParamSerializer, PostSerializer, PostEditSerializer, PostDetailSerializer
from core.models import User
from utils.commons import ReadOnly

sort_map = {
    'date': '-created_at',
    'views': '-views_count',
    'likes': '-likes_count',
}


class VideoListCreateAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request):
        page = request.GET.get('page', 1)
        rating = request.GET.get('rating', None)
        tag = request.GET.get('tag', '')
        sort = request.GET.get('sort', 'date')
        order_by = sort_map.get(sort, '-created_at')

        if rating:
            videos = Video.objects.filter(rating=rating).order_by(order_by)
        else:
            videos = Video.objects.all().order_by(order_by)

        if tag:
            videos = videos.filter(tags__name=tag)

        paginator = Paginator(videos, CONTENT_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = VideoSerializer(page_obj, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VideoPostSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.tags.add(*request.data.get('tags'))
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk): 
        video = get_object_or_404(Video, pk=pk)
        video.increment_views_count()
        serializer = VideoSerializer(video)
        return Response(serializer.data)

    def put(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        serializer = VideoPutSerializer(video, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page)
        return page_obj

    def get(self, request):
        filter = request.GET.get('filter', '')
        tag_name = request.GET.get('tag', '')

        tags = Tag.objects.all().order_by('name')
        if filter:
            tags = tags.filter(name__startswith=filter)
            page_obj = self.paginate_queryset(tags, CONTENT_PAGE_SIZE)
            serializer = TagSerializer(page_obj, many=True)
            return Response(serializer.data)
       
        if tag_name:
            tags = tags.filter(name__icontains=tag_name)

        page_obj = self.paginate_queryset(tags, CONTENT_PAGE_SIZE)
        serializer = TagSerializer(page_obj, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = TagSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try:
            data = JSONParser().parse(request)
            tag = get_object_or_404(Tag, pk=data['name'])
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except JSONDecodeError:
            return JsonResponse({"result": 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)


class ImageSlideListCreateAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request):
        page = request.GET.get('page', 1)
        rating = request.GET.get('rating', None)
        tag = request.GET.get('tag', '')
        sort = request.GET.get('sort', 'date')
        order_by = sort_map.get(sort, '-created_at')

        if rating:
            imageslides = ImageSlide.objects.filter(rating=rating).order_by(order_by)
        else:
            imageslides = ImageSlide.objects.all().order_by(order_by)

        if tag:
            imageslides = imageslides.filter(tags__name=tag)

        paginator = Paginator(imageslides, CONTENT_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = ImageSlideSerializer(page_obj, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ImageSlidePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            serializer = ImageSlideDetailSerializer(serializer.instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageSlideDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        imageslide = get_object_or_404(ImageSlide, pk=pk)
        imageslide.increment_views_count()
        serializer = ImageSlideDetailSerializer(imageslide, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        imageslide = get_object_or_404(ImageSlide, pk=pk)
        serializer = ImageSlidePutSerializer(imageslide, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ImageSlideDetailSerializer(serializer.instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        imageslide = get_object_or_404(ImageSlide, pk=pk)
        imageslide.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ImageListCreateAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, images_id):
        image_slide = get_object_or_404(ImageSlide, pk=images_id)
        page = request.GET.get('page', 1)

        image_list = Image.objects.all().order_by('-created_at')
        paginator = Paginator(image_list, CONTENT_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = ImageSerializer(page_obj, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, images_id):
        image_slide = get_object_or_404(ImageSlide, pk=images_id)
        serializer = ImagePostSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.tags.add(*request.data.get('tags'))
            serializer.save(slide=image_slide)
            response_serializer = ImageSerializer(serializer.instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]
    # parser_classes = [MultiPartParser, FormParser]

    def get(self, request, images_id, pk):
        image_slide = get_object_or_404(ImageSlide, pk=images_id)
        image = get_object_or_404(Image, pk=pk)
        serializer = ImageSerializer(image, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, images_id, pk):
        image = get_object_or_404(Image, pk=pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoLikeAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video_likes = video.likes.all().order_by('-created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(video_likes, SMALL_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = VideoLikeSerializer(page_obj, many=True)
        return Response(serializer.data)


    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video_like = VideoLike.objects.filter(video=video, user=request.user)
        if video_like:
            return Response({"result": 'error', 'message': 'You are already liked this video'}, status=status.HTTP_400_BAD_REQUEST)
        video_like = VideoLike.objects.create(video=video, user=request.user)
        video.increment_likes_count()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class VideoUnlikeAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video_like = VideoLike.objects.filter(video=video, user=request.user)
        if not video_like:
            return Response({"result": 'error', 'message': 'You are not liked this video'}, status=status.HTTP_400_BAD_REQUEST)
        video_like.delete()
        video.decrement_likes_count()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageSlideLikeAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, pk):
        image = get_object_or_404(ImageSlide, pk=pk)
        image_likes = image.likes.all().order_by('-created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(image_likes, SMALL_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = ImageSlideLikeSerializer(page_obj, many=True)
        return Response(serializer.data)


    def post(self, request, pk):
        slide = get_object_or_404(ImageSlide, pk=pk)
        images_like = ImageSlideLike.objects.filter(slide=slide, user=request.user)
        if images_like:
            return Response({"result": 'error', 'message': 'You are already liked this images'}, status=status.HTTP_400_BAD_REQUEST)
        images_like = ImageSlideLike.objects.create(slide=slide, user=request.user)
        slide.increment_likes_count()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageSlideUnLikeAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def post(self, request, pk):
        slide = get_object_or_404(ImageSlide, pk=pk)
        images_like = ImageSlideLike.objects.filter(slide=slide, user=request.user)
        if not images_like:
            return Response({"result": 'error', 'message': 'You are not liked this images'}, status=status.HTTP_400_BAD_REQUEST)
        images_like.delete()
        slide.decrement_likes_count()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoCommentListCreateAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, video_id):
        video = get_object_or_404(Video, pk=video_id)
        video_comments = video.comments.filter(parent_comment=None).order_by('created_at')

        query = VideoCommentParamSerializer(data=request.query_params)
        if query.is_valid():
            parent_comment_id = query.validated_data.get('parent')
            if parent_comment_id:
                video_comment = video.comments.filter(pk=parent_comment_id).first()
                if video_comment:
                    video_comments = video.comments.filter(parent_comment=parent_comment_id).order_by('created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(video_comments, SMALL_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = VideoCommentSerializer(page_obj, many=True)
        return Response(serializer.data)

    def post(self, request, video_id):
        try:
            video = get_object_or_404(Video, pk=video_id)
            data = JSONParser().parse(request)
            serializer = VideoCommentPostSerializer(data=data)
            if serializer.is_valid():
                parent_comment_id = serializer.validated_data.get('parent_comment_id')
                if parent_comment_id:
                    video_comment = video.comments.filter(pk=parent_comment_id).first()
                    if video_comment:
                        serializer.save(video=video, user=request.user, parent_comment=video_comment)   
                        response_serializer = VideoCommentSerializer(serializer.instance)
                        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"result": "error", "message": "Invalid parent comment id"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer.save(video=video, user=request.user)
                    response_serializer = VideoCommentSerializer(serializer.instance)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        

class VideoCommentDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def put(self, request, video_id, comment_id):
        try:
            video = get_object_or_404(Video, pk=video_id)
            data = JSONParser().parse(request)
            serializer = VideoCommentPutSerializer(data=data)
            if serializer.is_valid():
                video_comment = video.comments.filter(user=request.user, pk=comment_id).first()
                if video_comment:
                    video_comment.content = serializer.validated_data.get('content')
                    video_comment.save()
                    response_serializer = VideoCommentSerializer(video_comment)
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"result": "error", "message": "Invalid comment id"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, video_id, comment_id):
        try:
            video = get_object_or_404(Video, pk=video_id)
            video_comment = video.comments.filter(user=request.user, pk=comment_id).first()
            if video_comment:
                video_comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:    
                return Response({"result": "error", "message": "Invalid comment id"}, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class ImageSlideCommentListCreateAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, images_id):
        slide = get_object_or_404(ImageSlide, pk=images_id)
        image_comments = slide.comments.filter(parent_comment=None).order_by('created_at')

        query = ImageSlideCommentParamSerializer(data=request.query_params)
        if query.is_valid():
            parent_comment_id = query.validated_data.get('parent')
            if parent_comment_id:
                image_comment = slide.comments.filter(pk=parent_comment_id).first()
                if image_comment:
                    image_comments = slide.comments.filter(parent_comment=parent_comment_id).order_by('created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(image_comments, SMALL_PAGE_SIZE)
        page_obj = paginator.get_page(page)
        serializer = ImageSlideCommentSerializer(page_obj, many=True)
        return Response(serializer.data)

    def post(self, request, images_id):
        try:
            slide = get_object_or_404(ImageSlide, pk=images_id)
            data = JSONParser().parse(request)
            serializer = ImageSlideCommentPostSerializer(data=data)
            if serializer.is_valid():
                parent_comment_id = serializer.validated_data.get('parent_comment_id')
                if parent_comment_id:
                    image_comment = slide.comments.filter(pk=parent_comment_id).first()
                    if image_comment:
                        serializer.save(slide=slide, user=request.user, parent_comment=image_comment)   
                        response_serializer = ImageSlideCommentSerializer(serializer.instance)
                        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"result": "error", "message": "Invalid parent comment id"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer.save(slide=slide, user=request.user)
                    response_serializer = ImageSlideCommentSerializer(serializer.instance)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        

class ImageSlideCommentDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def put(self, request, images_id, comment_id):
        try:
            slide = get_object_or_404(ImageSlide, pk=images_id)
            data = JSONParser().parse(request)
            serializer = ImageSlideCommentPutSerializer(data=data)
            if serializer.is_valid():
                image_comment = slide.comments.filter(user=request.user, pk=comment_id).first()
                if image_comment:
                    image_comment.content = serializer.validated_data.get('content')
                    image_comment.save()
                    response_serializer = ImageSlideCommentSerializer(image_comment)
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"result": "error", "message": "Invalid comment id"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, images_id, comment_id):
        try:
            slide = get_object_or_404(ImageSlide, pk=images_id)
            image_comment = slide.comments.filter(user=request.user, pk=comment_id).first()
            if image_comment:
                image_comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:    
                return Response({"result": "error", "message": "Invalid comment id"}, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class PlaylistAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page)
        return page_obj

    def get(self, request):
        order_by = '-created_at'
        if request.user.is_authenticated:
            playlists = Playlist.objects.filter(user=request.user).order_by(order_by)
            page_obj = self.paginate_queryset(playlists, CONTENT_PAGE_SIZE)
            if request.query_params.get('type') == 'name':
                serializer = PlaylistNameSerializer(page_obj, many=True)
            else:
                serializer = PlaylistSerializer(page_obj, many=True)
            return Response(serializer.data)
        else:
            query = UserIDParamSerializer(data=request.query_params)
            if query.is_valid():
                user_id = query.validated_data.get('user_id')
                if user_id:
                    user = get_object_or_404(User, pk=user_id)
                    playlists = Playlist.objects.filter(user=user).order_by(order_by)
                    page_obj = self.paginate_queryset(playlists, CONTENT_PAGE_SIZE)
                    serializer = PlaylistSerializer(page_obj, many=True)
                    return Response(serializer.data)
            return Response([])

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            name = data.get('name')
            if not name:
                return Response({"result": 'error', 'message': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)
            playlist = Playlist.objects.filter(user=request.user, name=name)
            if playlist:
                return Response({"result": 'error', 'message': 'You already have a playlist with this name'}, status=status.HTTP_400_BAD_REQUEST)
            playlist = Playlist.objects.create(user=request.user, name=name)
            return Response({"result": 'success', 'message': f'You created a playlist {playlist.name}!'}, status=status.HTTP_200_OK)
        except JSONDecodeError:
            return JsonResponse({"result": 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)


class PlaylistDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        serializer = PlaylistDetailSerializer(playlist)
        return Response(serializer.data)

    def delete(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        playlist.delete()
        return Response({"result": 'success', 'message': f'You deleted the playlist {playlist.name}!'}, status=status.HTTP_200_OK)


class PlaylistVideoAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, playlist_id, video_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        video = get_object_or_404(Video, pk=video_id)
        playlist_video = playlist.videos.filter(pk=video_id)
        if playlist_video:
            return Response({"result": 'error', 'message': f'You already have the video {video.title} in the playlist {playlist.name}!'}, status=status.HTTP_400_BAD_REQUEST)
        playlist.videos.add(video)
        return Response({"result": 'success', 'message': f'You added the video {video.title} to the playlist {playlist.name}!'}, status=status.HTTP_200_OK)

    def delete(self, request, playlist_id, video_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        video = get_object_or_404(Video, pk=video_id)
        playlist_video = playlist.videos.filter(pk=video_id)
        if not playlist_video:
            return Response({"result": 'error', 'message': f'You don\'t have the video {video.title} in the playlist {playlist.name}!'}, status=status.HTTP_400_BAD_REQUEST)
        playlist.videos.remove(video)
        return Response({"result": 'success', 'message': f'You removed the video {video.title} from the playlist {playlist.name}!'}, status=status.HTTP_200_OK)


class PostAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page)
        return page_obj

    def get(self, request):
        order_by = '-created_at'
        if request.user.is_authenticated:
            posts = Post.objects.filter(user=request.user).order_by(order_by)
            page_obj = self.paginate_queryset(posts, CONTENT_PAGE_SIZE)
            serializer = PostSerializer(page_obj, many=True)
            return Response(serializer.data)
        else:
            query = UserIDParamSerializer(data=request.query_params)
            if query.is_valid():
                user_id = query.validated_data.get('user_id')
                if user_id:
                    user = get_object_or_404(User, pk=user_id)
                    posts = Post.objects.filter(user=user).order_by(order_by)
                    page_obj = self.paginate_queryset(posts, CONTENT_PAGE_SIZE)
                    serializer = PostSerializer(page_obj, many=True)
                    return Response(serializer.data)
            return Response([])

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = PostEditSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                serializer = PostDetailSerializer(serializer.instance)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"result": 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        

class PostDetailAPIView(views.APIView):
    permission_classes = [IsAuthenticated | ReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id, user=request.user)
        try:
            data = JSONParser().parse(request)
            serializer = PostEditSerializer(post, data=data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                serializer = PostDetailSerializer(serializer.instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"result": 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id, user=request.user)
        post.delete()
        return Response({"result": 'success', 'message': f'You deleted the post!'}, status=status.HTTP_200_OK)