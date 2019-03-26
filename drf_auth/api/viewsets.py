# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-many-ancestors,unused-argument,no-self-use,invalid-name
from django.contrib import auth
from rest_framework import viewsets
from rest_framework import response
from rest_framework import exceptions
from rest_framework import status
from applus.rest_framework import routers
from applus.django import dao
from .. import serializers


router = routers.VerbRouter()


@router.register_decorator("auth", base_name="api-auth", include="")
class AuthViewSet(viewsets.ViewSet):
    """ 登入/登出/帐号 """

    permission_classes = []

    token_dao = dao.cached_property_dao(
        "authtoken.token",
        "applus.rest_framework.authtoken.AuthTokenManager")

    @router.verb("POST")
    def login(self, request, *args, **kwargs):
        """ 登入 """
        serializer = serializers.LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.instance or not serializer.instance.id:
            raise exceptions.AuthenticationFailed
        auth.login(request, serializer.instance)
        #
        resp = self.profile(request, *args, **kwargs)
        resp.status_code = status.HTTP_201_CREATED
        return resp

    @router.verb("delete")
    def logout(self, request, *args, **kwargs):
        """ 登出 """
        if request.user and request.user.id:
            auth.logout(request)
        return response.Response({})

    @router.verb()
    def profile(self, request, *args, **kwargs):
        """ 帐号 """
        if not request.user or not request.user.id:
            return response.Response({})
        serializer = serializers.ProfileUserSerializer(instance=request.user)
        return response.Response(serializer.data)

    @router.verb()
    def token(self, request, *args, **kwargs):
        """ 令牌 """
        if not request.user or not request.user.id:
            return response.Response({})
        instance = self.token_dao.fetch(user_id=request.user.id)
        serializer = serializers.TokenSerializer(instance=instance)
        return response.Response(serializer.data)
