from supabase import create_client, Client
from typing import Optional, Dict, Any
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """Singleton service for Supabase interactions"""
    
    _instance: Optional['SupabaseService'] = None
    _client: Optional[Client] = None
    _service_client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None and settings.supabase_url and settings.supabase_anon_key:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase clients"""
        try:
            if not settings.supabase_url or not settings.supabase_anon_key:
                raise ValueError("Supabase configuration missing")
            # Public client (uses anon key)
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            
            # Service client (uses service key) - for admin operations
            if settings.supabase_service_key:
                self._service_client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )            
            logger.info("Supabase clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase clients: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the public Supabase client"""
        if self._client is None:
            if not settings.supabase_url or not settings.supabase_anon_key:
                raise ValueError("Supabase configuration missing")
            self._initialize_clients()
        return self._client

    @property
    def service_client(self) -> Client:
        """Get the service Supabase client (admin operations)"""
        if self._service_client is None:
            if not settings.supabase_url or not settings.supabase_service_key:
                raise ValueError("Supabase service configuration missing")
            self._initialize_clients()
        return self._service_client
    
    async def create_user(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user with Supabase Auth"""
        try:
            response = self.service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": False,
                "user_metadata": user_data
            })
            return response.user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            logger.error(f"Failed to sign in user: {e}")
            raise
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out a user"""
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Failed to sign out user: {e}")
            return False
    
    async def verify_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            user = self.client.auth.get_user(access_token)
            return user.user if user else None
        except Exception as e:
            logger.error(f"Failed to verify token: {e}")
            return None

# Singleton instance
supabase_service = SupabaseService()