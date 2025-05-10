from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

# Instead of importing modules directly, define a function to register routes
def register_routes():
    # Import routes here to avoid circular imports
    from . import login       # Auth-related endpoints
    from . import register    # Auth-related endpoints
    from . import test
    # Remove non-existent imports
    # from . import product
    # from . import recommend
    # from . import search
    from . import tryon
    from . import chat
    from . import trends
    from . import keywords
    from . import profile
    from . import social
    from . import outfits
    from . import gemini
    
    # Return the blueprint after all routes are registered
    return api_blueprint

