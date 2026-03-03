from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

from identity.domain.interfaces import GoogleAuthServiceInterface

class GoogleAuthService(GoogleAuthServiceInterface):
    def verify_google_token(self, token: str) -> dict:
        try:
            # Requires GOOGLE_CLIENT_ID to be configured in Django settings
            client_id = getattr(settings, "GOOGLE_CLIENT_ID", None)
            print(f"--- GoogleAuthService ---")
            print(f"Token length: {len(token) if token else 0}")
            print(f"Client ID in settings: {client_id}")
            
            if not client_id:
                raise ValueError("GOOGLE_CLIENT_ID is not configured in settings.")
            
            idinfo = id_token.verify_oauth2_token(
                id_token=token,
                request=requests.Request(),
                audience=client_id,
                clock_skew_in_seconds=60
            )
            print(f"Token verified successfully. Email: {idinfo.get('email')}")
            print(f"-------------------------")
            return idinfo
        except ValueError as e:
            print(f"Google Token Verification Error (ValueError): {str(e)}")
            raise ValueError(f"Invalid Google token: {str(e)}")
        except Exception as e:
            print(f"Google Token Verification CRITICAL Error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Unexpected error verifying token: {str(e)}")
