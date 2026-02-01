from .auth import router as auth_router
from .autocall import router as autocall_router
from .family import router as family_router
from .hospitals import router as hospitals_router
from .profiles import router as profiles_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
    "profiles_router",
    "hospitals_router",
    "family_router",
    "autocall_router",
]
