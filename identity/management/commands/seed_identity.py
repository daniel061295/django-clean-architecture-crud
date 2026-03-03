"""
Django management command to seed identity data (permissions, roles, users).

Uses application use cases to ensure business logic is properly applied,
including automatic assignment of default user avatars.
"""
from django.core.management.base import BaseCommand
from injector import Injector

from config.di import create_injector
from identity.application.dtos import CreatePermissionInputDTO, CreateRoleInputDTO, CreateUserInputDTO
from identity.application.use_cases import CreatePermission, CreateRole, CreateUser
from identity.domain.exceptions import PermissionAlreadyExistsError, RoleAlreadyExistsError


class Command(BaseCommand):
    """Command to seed the database with permissions, roles, and test users."""

    help = "Seed the database with permissions, roles, and test users"

    # Permission definitions
    PERMISSIONS_DATA = [
        {"code": "scan_plant", "description": "Can perform plant scans"},
        {"code": "view_ads", "description": "Must view ads before scanning"},
        {"code": "bypass_ads", "description": "Can skip ads before scanning"},
        {"code": "manage_subscriptions", "description": "Can manage user subscriptions"},
        {"code": "manage_users", "description": "Can manage users"},
        {"code": "admin_access", "description": "Full system access"},
        {"code": "view_all_history", "description": "Can view all user history records"},
    ]

    # Role definitions with their permissions
    ROLES_DATA = {
        "admin": [
            "scan_plant",
            "bypass_ads",
            "manage_subscriptions",
            "manage_users",
            "admin_access",
            "view_all_history",
        ],
        "subscriber": ["scan_plant", "bypass_ads"],
        "free_user": ["scan_plant", "view_ads"],
    }

    # User definitions with their roles
    USERS_DATA = [
        {
            "email": "daniel061295@gmail.com",
            "username": "daniel061295",
            "roles": ["admin"],
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "subscriber@test.com",
            "username": "subscriber",
            "roles": ["subscriber"],
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "email": "freeuser@test.com",
            "username": "freeuser",
            "roles": ["free_user"],
            "is_staff": False,
            "is_superuser": False,
        },
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.injector: Injector = None

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Starting identity seed...\n")

        # Initialize injector for use case dependencies
        self.injector = create_injector()

        # Step 1: Create permissions
        self.stdout.write("Step 1: Creating permissions...")
        permission_use_case = self.injector.get(CreatePermission)
        
        for perm_data in self.PERMISSIONS_DATA:
            try:
                input_dto = CreatePermissionInputDTO(**perm_data)
                permission_use_case.execute(input_dto)
                self.stdout.write(self.style.SUCCESS(f"  [CREATED] {perm_data['code']}"))
            except PermissionAlreadyExistsError:
                self.stdout.write(self.style.WARNING(f"  [EXISTS] {perm_data['code']}"))

        # Step 2: Create roles with their permissions
        self.stdout.write("\nStep 2: Creating roles...")
        role_use_case = self.injector.get(CreateRole)
        
        for role_name, perm_codes in self.ROLES_DATA.items():
            try:
                input_dto = CreateRoleInputDTO(name=role_name, permission_codes=perm_codes)
                role_use_case.execute(input_dto)
                self.stdout.write(self.style.SUCCESS(f"  [CREATED] {role_name} ({len(perm_codes)} permissions)"))
            except RoleAlreadyExistsError:
                self.stdout.write(self.style.WARNING(f"  [EXISTS] {role_name}"))

        # Step 3: Create users with their roles (using use case for avatar assignment)
        self.stdout.write("\nStep 3: Creating users (with default avatar)...")
        user_use_case = self.injector.get(CreateUser)
        
        for user_data in self.USERS_DATA:
            try:
                input_dto = CreateUserInputDTO(
                    email=user_data["email"],
                    username=user_data["username"],
                    password="Test123!",
                    role_names=user_data["roles"],
                )
                user_use_case.execute(input_dto)
                role_names = ", ".join(user_data["roles"])
                self.stdout.write(self.style.SUCCESS(f"  [CREATED] {user_data['email']} (roles: {role_names}) - with default avatar"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  [EXISTS] {user_data['email']} - {str(e)}"))

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded identity data!"))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: New users have been assigned the default password: Test123!\n"
                "All users have been assigned the default avatar image."
            )
        )
