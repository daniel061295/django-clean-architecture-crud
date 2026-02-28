"""
Django management command to seed identity data (permissions, roles, users).
"""
from django.core.management.base import BaseCommand

from identity.models import CustomUserModel, PermissionModel, RoleModel


class Command(BaseCommand):
    """Command to seed the database with permissions, roles, and users."""

    help = "Seed the database with permissions, roles, and test users"

    # Permission definitions
    PERMISSIONS_DATA = [
        {"code": "scan_plant", "description": "Can perform plant scans"},
        {"code": "view_ads", "description": "Must view ads before scanning"},
        {"code": "bypass_ads", "description": "Can skip ads before scanning"},
        {"code": "manage_subscriptions", "description": "Can manage user subscriptions"},
        {"code": "manage_users", "description": "Can manage users"},
        {"code": "admin_access", "description": "Full system access"},
    ]

    # Role definitions with their permissions
    ROLES_DATA = {
        "admin": [
            "scan_plant",
            "bypass_ads",
            "manage_subscriptions",
            "manage_users",
            "admin_access",
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

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Starting identity seed...\n")

        # Step 1: Create permissions
        self.stdout.write("Step 1: Creating permissions...")
        permissions_map = {}
        for perm_data in self.PERMISSIONS_DATA:
            perm, created = PermissionModel.objects.update_or_create(
                code=perm_data["code"],
                defaults={"description": perm_data["description"]},
            )
            permissions_map[perm_data["code"]] = perm
            status = "CREATED" if created else "UPDATED"
            self.stdout.write(self.style.SUCCESS(f"  [{status}] {perm.code}"))

        # Step 2: Create roles with their permissions
        self.stdout.write("\nStep 2: Creating roles...")
        roles_map = {}
        for role_name, perm_codes in self.ROLES_DATA.items():
            role, created = RoleModel.objects.update_or_create(
                name=role_name,
                defaults={},
            )
            # Set permissions for the role
            role_permissions = [permissions_map[code] for code in perm_codes]
            role.permissions.set(role_permissions)
            roles_map[role_name] = role
            status = "CREATED" if created else "UPDATED"
            self.stdout.write(
                self.style.SUCCESS(f"  [{status}] {role.name} ({len(perm_codes)} permissions)")
            )

        # Step 3: Create users with their roles
        self.stdout.write("\nStep 3: Creating users...")
        for user_data in self.USERS_DATA:
            user, created = CustomUserModel.objects.update_or_create(
                email=user_data["email"],
                defaults={
                    "username": user_data["username"],
                    "is_staff": user_data.get("is_staff", False),
                    "is_superuser": user_data.get("is_superuser", False),
                    "is_active": True,
                },
            )
            # Set a default password if user is new
            if created:
                user.set_password("Test123!")
                user.save()

            # Set roles for the user
            user_roles = [roles_map[role_name] for role_name in user_data["roles"]]
            user.roles.set(user_roles)

            status = "CREATED" if created else "UPDATED"
            role_names = ", ".join(user_data["roles"])
            self.stdout.write(
                self.style.SUCCESS(f"  [{status}] {user.email} (roles: {role_names})")
            )

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded identity data!"))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: New users have been assigned the default password: Test123!"
            )
        )
