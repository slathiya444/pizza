from functools import wraps
from fastapi import HTTPException, Depends
from .auth import get_current_user
from .models import UserResponse


def authorize_role(allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: UserResponse = kwargs.get('current_user')
            if not current_user:
                current_user = await get_current_user()

            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Not authorized")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Usage in your route
@router.post("/pizzas", response_model=PizzaResponse)
@authorize_role(["admin", "chef"])  # Specify the allowed roles
def create_pizza(
        pizza: PizzaCreate,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    # Your existing function logic here
    pass