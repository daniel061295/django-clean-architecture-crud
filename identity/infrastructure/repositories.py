"""
Identity Infrastructure Repositories — Django ORM implementations of domain interfaces.
"""
from typing import List, Optional
from uuid import UUID

from identity.domain.entities import Permission, Role, User
from identity.domain.interfaces import PermissionRepository, RoleRepository, UserRepository
from identity.infrastructure.mappers import PermissionMapper, RoleMapper, UserMapper
from identity.infrastructure.models import CustomUserModel, PermissionModel, RoleModel


class DjangoPermissionRepository(PermissionRepository):
    """Django ORM implementation of PermissionRepository."""

    def save(self, permission: Permission) -> Permission:
        """Creates or updates a permission record."""
        model, _ = PermissionModel.objects.update_or_create(
            code=permission.code,
            defaults={"description": permission.description},
        )
        return PermissionMapper.to_domain(model)

    def get_by_code(self, code: str) -> Optional[Permission]:
        """Retrieves a permission by code. Returns None if not found."""
        try:
            model = PermissionModel.objects.get(code=code)
            return PermissionMapper.to_domain(model)
        except PermissionModel.DoesNotExist:
            return None

    def list_all(self) -> List[Permission]:
        """Returns all permissions."""
        return [PermissionMapper.to_domain(m) for m in PermissionModel.objects.all()]

    def exists_by_code(self, code: str) -> bool:
        """Returns True if a permission with the given code exists."""
        return PermissionModel.objects.filter(code=code).exists()


class DjangoRoleRepository(RoleRepository):
    """Django ORM implementation of RoleRepository."""

    def save(self, role: Role) -> Role:
        """Creates or updates a role record with its permissions."""
        model, _ = RoleModel.objects.update_or_create(
            id=role.id,
            defaults={"name": role.name},
        )
        # Sync permissions
        permission_codes = [p.code for p in role.permissions]
        permission_models = PermissionModel.objects.filter(code__in=permission_codes)
        model.permissions.set(permission_models)
        model.save()
        model.refresh_from_db()
        model_with_perms = RoleModel.objects.prefetch_related("permissions").get(id=model.id)
        return RoleMapper.to_domain(model_with_perms)

    def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Retrieves a role by UUID including permissions."""
        try:
            model = RoleModel.objects.prefetch_related("permissions").get(id=role_id)
            return RoleMapper.to_domain(model)
        except RoleModel.DoesNotExist:
            return None

    def get_by_name(self, name: str) -> Optional[Role]:
        """Retrieves a role by name."""
        try:
            model = RoleModel.objects.prefetch_related("permissions").get(name=name)
            return RoleMapper.to_domain(model)
        except RoleModel.DoesNotExist:
            return None

    def list_all(self) -> List[Role]:
        """Returns all roles with their permissions."""
        models = RoleModel.objects.prefetch_related("permissions").all()
        return [RoleMapper.to_domain(m) for m in models]

    def exists_by_name(self, name: str) -> bool:
        """Returns True if a role with the given name exists."""
        return RoleModel.objects.filter(name=name).exists()

    def add_permission_to_role(self, role_id: UUID, permission_code: str) -> Role:
        """Adds a permission to a role. Returns the updated role."""
        role_model = RoleModel.objects.prefetch_related("permissions").get(id=role_id)
        perm_model = PermissionModel.objects.get(code=permission_code)
        role_model.permissions.add(perm_model)
        role_model.refresh_from_db()
        updated = RoleModel.objects.prefetch_related("permissions").get(id=role_id)
        return RoleMapper.to_domain(updated)


class DjangoUserRepository(UserRepository):
    """Django ORM implementation of UserRepository."""

    def _get_with_roles(self, user_model: CustomUserModel) -> User:
        """Helper: fetch user with all nested relations prefetched."""
        user_model = (
            CustomUserModel.objects.prefetch_related("roles__permissions")
            .get(id=user_model.id)
        )
        return UserMapper.to_domain(user_model)

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieves a user by UUID with roles and permissions."""
        try:
            model = CustomUserModel.objects.prefetch_related("roles__permissions").get(id=user_id)
            return UserMapper.to_domain(model)
        except CustomUserModel.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user by email."""
        try:
            model = CustomUserModel.objects.prefetch_related("roles__permissions").get(email=email)
            return UserMapper.to_domain(model)
        except CustomUserModel.DoesNotExist:
            return None

    def list_all(self) -> List[User]:
        """Returns all users with roles and permissions."""
        models = CustomUserModel.objects.prefetch_related("roles__permissions").all()
        return [UserMapper.to_domain(m) for m in models]

    def assign_role(self, user_id: UUID, role_id: UUID) -> User:
        """Assigns a role to a user. Returns updated user entity."""
        user_model = CustomUserModel.objects.get(id=user_id)
        role_model = RoleModel.objects.get(id=role_id)
        user_model.roles.add(role_model)
        return self._get_with_roles(user_model)

    def remove_role(self, user_id: UUID, role_id: UUID) -> User:
        """Removes a role from a user. Returns updated user entity."""
        user_model = CustomUserModel.objects.get(id=user_id)
        role_model = RoleModel.objects.get(id=role_id)
        user_model.roles.remove(role_model)
        return self._get_with_roles(user_model)
