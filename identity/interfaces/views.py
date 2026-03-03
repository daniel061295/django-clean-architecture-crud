"""
Identity Interface Views — DRF ViewSets for RBAC management.

All endpoints require HasPermission('manage_users') for admin operations.
Views are dumb: they delegate all logic to use cases via injected dependencies.
"""
from uuid import UUID

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from injector import inject
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from identity.interfaces.permissions import HasPermission
from identity.application.dtos import (
    AssignPermissionToRoleInputDTO,
    AssignRoleToUserInputDTO,
    AuthenticateWithGoogleInputDTO,
    CreatePermissionInputDTO,
    CreateRoleInputDTO,
    CreateUserInputDTO,
    DeleteUserAvatarInputDTO,
    GetUserPermissionsInputDTO,
    GetUserProfileInputDTO,
    RemoveRoleFromUserInputDTO,
    UpdateUserAvatarInputDTO,
)
from identity.application.use_cases import (
    AssignPermissionToRole,
    AssignRoleToUser,
    AuthenticateWithGoogle,
    CheckUserPermission,
    CreatePermission,
    CreateRole,
    CreateUser,
    DeleteUserAvatar,
    GetUser,
    GetUserPermissions,
    GetUserProfile,
    ListPermissions,
    ListRoles,
    ListUsers,
    RemoveRoleFromUser,
    UpdateUserAvatar,
)
from identity.domain.exceptions import AvatarValidationError, UserNotFoundError
from identity.interfaces.serializers import (
    AssignPermissionToRoleInputSerializer,
    AssignRoleToUserInputSerializer,
    GoogleLoginInputSerializer,
    PermissionInputSerializer,
    PermissionOutputSerializer,
    RoleInputSerializer,
    RoleOutputSerializer,
    UserAvatarInputSerializer,
    UserAvatarOutputSerializer,
    UserCreateInputSerializer,
    UserOutputSerializer,
    UserProfileOutputSerializer,
)


class UserPermissionsOutputSerializer(serializers.Serializer):
    """Serializer for user permissions output."""

    permissions = serializers.ListField(child=serializers.CharField())

    def to_representation(self, instance):
        """Convert DTO to representation."""
        if hasattr(instance, "permissions"):
            data = {"permissions": instance.permissions}
        else:
            data = instance
        return super().to_representation(data)


class PermissionViewSet(viewsets.ViewSet):
    """ViewSet for managing system permissions (requires manage_users permission)."""

    permission_classes = [HasPermission]

    def get_permission_code(self) -> str:
        """Returns the required permission code for this endpoint."""
        return "manage_users"

    @inject
    def __init__(
        self,
        create_permission: CreatePermission = None,
        list_permissions: ListPermissions = None,
        **kwargs,
    ) -> None:
        self._create = create_permission
        self._list = list_permissions
        super().__init__(**kwargs)

    @extend_schema(request=PermissionInputSerializer, responses={201: PermissionOutputSerializer})
    def create(self, request: Request) -> Response:
        """Creates a new system permission."""
        serializer = PermissionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreatePermissionInputDTO(**serializer.validated_data)
        result = self._create.execute(input_dto)

        return Response(PermissionOutputSerializer(result).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: PermissionOutputSerializer(many=True)})
    def list(self, request: Request) -> Response:
        """Returns all system permissions."""
        results = self._list.execute()
        return Response(PermissionOutputSerializer(results, many=True).data)


@extend_schema_view(
    assign_permission=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)]),
)
class RoleViewSet(viewsets.ViewSet):
    """ViewSet for managing roles (requires manage_users permission)."""

    permission_classes = [HasPermission]

    def get_permission_code(self) -> str:
        """Returns the required permission code for this endpoint."""
        return "manage_users"

    @inject
    def __init__(
        self,
        create_role: CreateRole = None,
        list_roles: ListRoles = None,
        assign_permission: AssignPermissionToRole = None,
        **kwargs,
    ) -> None:
        self._create = create_role
        self._list = list_roles
        self._assign_permission = assign_permission
        super().__init__(**kwargs)

    @extend_schema(request=RoleInputSerializer, responses={201: RoleOutputSerializer})
    def create(self, request: Request) -> Response:
        """Creates a new role with optional permissions."""
        serializer = RoleInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreateRoleInputDTO(**serializer.validated_data)
        result = self._create.execute(input_dto)

        return Response(RoleOutputSerializer(result).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: RoleOutputSerializer(many=True)})
    def list(self, request: Request) -> Response:
        """Returns all roles with their permissions."""
        results = self._list.execute()
        return Response(RoleOutputSerializer(results, many=True).data)

    @extend_schema(
        request=AssignPermissionToRoleInputSerializer,
        responses={200: RoleOutputSerializer},
    )
    @action(detail=True, methods=["post"], url_path="assign-permission")
    def assign_permission(self, request: Request, pk: str = None) -> Response:
        """Adds a permission to a role."""
        serializer = AssignPermissionToRoleInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = AssignPermissionToRoleInputDTO(
            role_id=UUID(pk),
            permission_code=serializer.validated_data["permission_code"],
        )
        result = self._assign_permission.execute(input_dto)
        return Response(RoleOutputSerializer(result).data)


@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)]),
    assign_role=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)]),
    remove_role=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)]),
)
class UserViewSet(viewsets.ViewSet):
    """ViewSet for managing users (requires manage_users permission)."""

    def get_permissions(self):
        """Allows public registration for 'create', requires admin for the rest."""
        from rest_framework.permissions import AllowAny
        if self.action == 'create':
            return [AllowAny()]
        return [HasPermission()]

    def get_permission_code(self) -> str:
        """Returns the required permission code for this endpoint."""
        return "manage_users"

    @inject
    def __init__(
        self,
        create_user: CreateUser = None,
        list_users: ListUsers = None,
        get_user: GetUser = None,
        assign_role: AssignRoleToUser = None,
        remove_role: RemoveRoleFromUser = None,
        **kwargs,
    ) -> None:
        self._create = create_user
        self._list = list_users
        self._get = get_user
        self._assign_role = assign_role
        self._remove_role = remove_role
        super().__init__(**kwargs)

    @extend_schema(request=UserCreateInputSerializer, responses={201: UserOutputSerializer})
    def create(self, request: Request) -> Response:
        """Creates a new user with optional roles."""
        serializer = UserCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreateUserInputDTO(**serializer.validated_data)
        result = self._create.execute(input_dto)
        return Response(UserOutputSerializer(result).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: UserOutputSerializer(many=True)})
    def list(self, request: Request) -> Response:
        """Returns all users with their roles."""
        results = self._list.execute()
        return Response(UserOutputSerializer(results, many=True).data)

    @extend_schema(responses={200: UserOutputSerializer})
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """Returns a single user by UUID."""
        result = self._get.execute(UUID(pk))
        return Response(UserOutputSerializer(result).data)

    @extend_schema(
        request=AssignRoleToUserInputSerializer,
        responses={200: UserOutputSerializer},
    )
    @action(detail=True, methods=["post"], url_path="assign-role")
    def assign_role(self, request: Request, pk: str = None) -> Response:
        """Assigns a role to a user."""
        serializer = AssignRoleToUserInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = AssignRoleToUserInputDTO(
            user_id=UUID(pk),
            role_id=serializer.validated_data["role_id"],
        )
        result = self._assign_role.execute(input_dto)
        return Response(UserOutputSerializer(result).data)

    @extend_schema(
        request=AssignRoleToUserInputSerializer,
        responses={200: UserOutputSerializer},
    )
    @action(detail=True, methods=["post"], url_path="remove-role")
    def remove_role(self, request: Request, pk: str = None) -> Response:
        """Removes a role from a user."""
        serializer = AssignRoleToUserInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = RemoveRoleFromUserInputDTO(
            user_id=UUID(pk),
            role_id=serializer.validated_data["role_id"],
        )
        result = self._remove_role.execute(input_dto)
        return Response(UserOutputSerializer(result).data)


class MyPermissionsView(APIView):
    """GET /identity/me/permissions — Returns current user's permissions."""

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(
        self,
        get_user_permissions: GetUserPermissions = None,
        **kwargs,
    ) -> None:
        self._get_user_permissions = get_user_permissions
        super().__init__(**kwargs)

    @extend_schema(responses={200: UserPermissionsOutputSerializer})
    def get(self, request: Request) -> Response:
        """Returns all permission codes granted to the current user."""
        input_dto = GetUserPermissionsInputDTO(user_id=request.user.id)
        result = self._get_user_permissions.execute(input_dto)
        return Response(UserPermissionsOutputSerializer(result).data)


class UserProfileView(APIView):
    """
    GET /identity/me/ — Returns current user's full profile.
    PUT /identity/me/ — Updates current user's profile (future extension).
    """

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(
        self,
        get_user_profile: GetUserProfile = None,
        **kwargs,
    ) -> None:
        self._get_user_profile = get_user_profile
        super().__init__(**kwargs)

    @extend_schema(responses={200: UserProfileOutputSerializer})
    def get(self, request: Request) -> Response:
        """Returns the current user's full profile including avatar, roles, and permissions."""
        input_dto = GetUserProfileInputDTO(user_id=request.user.id)
        result = self._get_user_profile.execute(input_dto)
        return Response(UserProfileOutputSerializer(result).data)


class UserAvatarView(APIView):
    """
    POST /identity/me/avatar/ — Uploads or updates the current user's avatar.
    DELETE /identity/me/avatar/ — Deletes the current user's avatar.
    """

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(
        self,
        update_user_avatar: UpdateUserAvatar = None,
        delete_user_avatar: DeleteUserAvatar = None,
        **kwargs,
    ) -> None:
        self._update_user_avatar = update_user_avatar
        self._delete_user_avatar = delete_user_avatar
        super().__init__(**kwargs)

    @extend_schema(
        request=UserAvatarInputSerializer,
        responses={
            200: UserAvatarOutputSerializer,
            400: {"description": "Bad Request - Invalid avatar format"},
        },
    )
    def post(self, request: Request) -> Response:
        """Uploads or updates the current user's avatar."""
        serializer = UserAvatarInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_base64 = serializer.validated_data["avatar"]
        input_dto = UpdateUserAvatarInputDTO(
            user_id=request.user.id,
            avatar_base64=avatar_base64,
        )
        
        try:
            result = self._update_user_avatar.execute(input_dto)
            return Response(UserAvatarOutputSerializer(result).data)
        except AvatarValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(responses={200: UserAvatarOutputSerializer})
    def delete(self, request: Request) -> Response:
        """Deletes the current user's avatar."""
        try:
            input_dto = DeleteUserAvatarInputDTO(user_id=request.user.id)
            result = self._delete_user_avatar.execute(input_dto)
            return Response(UserAvatarOutputSerializer(result).data)
        except UserNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


class GoogleLoginView(APIView):
    """
    POST /auth/google/ — Authenticates a user via Google OAuth and returns JWT tokens.
    """
    permission_classes = []  # Public endpoint

    @inject
    def __init__(
        self,
        authenticate_google: AuthenticateWithGoogle = None,
        **kwargs,
    ) -> None:
        self._authenticate_google = authenticate_google
        super().__init__(**kwargs)

    @extend_schema(
        request=GoogleLoginInputSerializer,
        responses={
            200: {"description": "OK - Returns access and refresh tokens"},
            400: {"description": "Bad Request - Invalid token"},
        },
    )
    def post(self, request: Request) -> Response:
        """Verifies a Google OAuth token and returns local JWT tokens."""
        print("=== GOOGLE LOGIN REQUEST RECIBIDO ===")
        print("Headers:", request.headers)
        print("Data:", request.data)
        print("=====================================")
        
        serializer = GoogleLoginInputSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print("=== SERIALIZER ERROR ===")
            print(serializer.errors)
            print("========================")
            raise

        try:
            input_dto = AuthenticateWithGoogleInputDTO(
                token=serializer.validated_data["token"]
            )
            user_domain = self._authenticate_google.execute(input_dto)
            
            # Fetch the actual Django user model to generate tokens
            from identity.infrastructure.models import CustomUserModel
            user_model = CustomUserModel.objects.get(id=user_domain.id)
            
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user_model)
            
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            print("=== VALUE ERROR ===")
            print(str(e))
            print("===================")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("=== UNEXPECTED ERROR ===")
            import traceback
            traceback.print_exc()
            print("========================")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
