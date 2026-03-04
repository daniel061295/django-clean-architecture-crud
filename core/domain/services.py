from abc import ABC, abstractmethod
from typing import Optional


class StorageServiceInterface(ABC):
    """
    Interface for unified storage services (e.g. Cloudflare R2, AWS S3).
    Follows Clean Architecture by decoupling business logic from storage specifics.
    """

    @abstractmethod
    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        """
        Uploads a file and returns its unique identifier (e.g. an object key).
        
        Args:
            file_data: The binary data of the file.
            file_name: The destination path/name (e.g., 'avatars/user123.jpg').
            content_type: The MIME type of the file.
            
        Returns:
            The unique identifier of the uploaded file.
        """
        pass

    @abstractmethod
    def delete_file(self, file_identifier: str) -> bool:
        """
        Deletes a file given its identifier.
        """
        pass

    @abstractmethod
    def get_signed_url(self, file_identifier: str, expires_in_seconds: int = 3600) -> Optional[str]:
        """
        Generates a temporary signed URL to securely access the file payload over HTTP.
        """
        pass
