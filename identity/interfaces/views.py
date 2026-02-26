"""
Identity Interface Views — DRF ViewSets for RBAC management.

All endpoints are protected by IsAdminUser. Views are dumb:
they delegate all logic to use cases via injected dependencies.
"""
from uuid import UUID

from drf_spectacular.utils import extend_schema, extend_schema_view
from injector import inject
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from identity.application.dtos import (
    AssignPermissionToRoleInputDTO,
    AssignRoleToUserInputDTO,
    CreatePermissionInputDTO,
    CreateRoleInputDTO,
    CreateUserInputDTO,
    RemoveRoleFromUserInputDTO,
)
from identity.application.use_cases import (
    AssignPermissionToRole,
    AssignRoleToUser,
    CreatePermission,
    CreateRole,
    CreateUser,
    GetUser,
    ListPermissions,
    ListRoles,
    ListUsers,
    RemoveRoleFromUser,
)
from identity.interfaces.serializers import (
    AssignPermissionToRoleInputSerializer,
    AssignRoleToUserInputSerializer,
    PermissionInputSerializer,
    PermissionOutputSerializer,
    RoleInputSerializer,
    RoleOutputSerializer,
    UserCreateInputSerializer,
    UserOutputSerializer,
)


class PermissionViewSet(viewsets.ViewSet):
    """ViewSet for managing system permissions (admin only)."""

    permission_classes = [IsAdminUser]

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


class RoleViewSet(viewsets.ViewSet):
    """ViewSet for managing roles (admin only)."""

    permission_classes = [IsAdminUser]

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


class UserViewSet(viewsets.ViewSet):
    """ViewSet for managing users (admin only)."""

    permission_classes = [IsAdminUser]

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
