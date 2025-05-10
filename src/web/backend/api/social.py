from flask import request, jsonify, current_app
from . import api_blueprint
import jwt
import os
import json
from models.social import Post, Comment, Like, OutfitChallenge, ChallengeEntry, StylistConsultation, FollowRelationship
from datetime import datetime
import uuid

# Helper function to verify token
def verify_token(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

#
# Community Feed Endpoints
#

@api_blueprint.route('/social/feed', methods=['GET'])
def get_community_feed():
    """Get the community feed posts"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Optional parameters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    
    try:
        # Get feed posts
        posts = Post.get_feed(page=page, limit=limit)
        
        return jsonify({
            "message": "Posts retrieved successfully",
            "data": {
                "posts": [post.to_dict() for post in posts],
                "page": page,
                "limit": limit,
                "total": len(posts)  # In a real app, you'd return actual total count
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving feed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/posts', methods=['POST'])
def create_post():
    """Create a new community post"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ['content']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        post = Post(
            user_id=user_id,
            content=data['content'],
            title=data.get('title', ''),
            image_urls=data.get('image_urls', []),
            outfit_items=data.get('outfit_items', []),
            tags=data.get('tags', []),
            visibility=data.get('visibility', 'public')
        )
        
        post.save()
        
        return jsonify({
            "message": "Post created successfully",
            "data": post.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error creating post: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    try:
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        return jsonify({
            "message": "Post retrieved successfully",
            "data": post.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving post: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like a post"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    try:
        # Check if post exists
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Check if already liked
        existing_like = Like.user_has_liked(user_id, post_id, 'post')
        if existing_like:
            return jsonify({"error": "You have already liked this post"}), 400
        
        # Create like
        like = Like(
            user_id=user_id,
            target_id=post_id,
            target_type='post'
        )
        
        like.save()
        
        # Update post like count
        post.like()
        
        return jsonify({
            "message": "Post liked successfully"
        })
    except Exception as e:
        current_app.logger.error(f"Error liking post: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/posts/<post_id>/comment', methods=['POST'])
def comment_on_post(post_id):
    """Comment on a post"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data or 'content' not in data:
        return jsonify({"error": "No comment content provided"}), 400
    
    try:
        # Check if post exists
        post = Post.get_by_id(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Create comment
        comment = Comment(
            user_id=user_id,
            post_id=post_id,
            content=data['content']
        )
        
        comment.save()
        
        # Update post comment count
        post.comment()
        
        return jsonify({
            "message": "Comment added successfully",
            "data": comment.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error adding comment: {str(e)}")
        return jsonify({"error": str(e)}), 500

#
# Outfit Challenge Endpoints
#

@api_blueprint.route('/challenges', methods=['GET'])
def get_challenges():
    """Get available outfit challenges"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    # Optional filter parameter
    status = request.args.get('status', 'active')  # active, upcoming, past
    
    try:
        if status == 'active':
            challenges = OutfitChallenge.get_active_challenges()
        elif status == 'upcoming':
            challenges = OutfitChallenge.get_upcoming_challenges()
        elif status == 'past':
            challenges = OutfitChallenge.get_past_challenges()
        else:
            challenges = OutfitChallenge.get_all_challenges()
        
        return jsonify({
            "message": "Challenges retrieved successfully",
            "data": [challenge.to_dict() for challenge in challenges]
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving challenges: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/challenges/<challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """Get a specific outfit challenge details"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    try:
        challenge = OutfitChallenge.get_by_id(challenge_id)
        if not challenge:
            return jsonify({"error": "Challenge not found"}), 404
        
        # Get entries for this challenge
        entries = ChallengeEntry.get_challenge_entries(challenge_id)
        
        return jsonify({
            "message": "Challenge retrieved successfully",
            "data": {
                "challenge": challenge.to_dict(),
                "entries": [entry.to_dict() for entry in entries]
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving challenge: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/challenges/<challenge_id>/enter', methods=['POST'])
def enter_challenge(challenge_id):
    """Submit an outfit entry for a challenge"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ['title', 'image_urls']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Check if challenge exists and is active
        challenge = OutfitChallenge.get_by_id(challenge_id)
        if not challenge:
            return jsonify({"error": "Challenge not found"}), 404
        
        if challenge.status != 'active':
            return jsonify({"error": "This challenge is not currently active"}), 400
        
        # Create challenge entry
        entry = ChallengeEntry(
            challenge_id=challenge_id,
            user_id=user_id,
            title=data['title'],
            description=data.get('description', ''),
            image_urls=data['image_urls'],
            outfit_items=data.get('outfit_items', [])
        )
        
        entry.save()
        
        # Update challenge entry count
        challenge.add_entry()
        
        return jsonify({
            "message": "Challenge entry submitted successfully",
            "data": entry.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error submitting challenge entry: {str(e)}")
        return jsonify({"error": str(e)}), 500

#
# AI Stylist Consultation Endpoints
#

@api_blueprint.route('/stylist/consultations', methods=['POST'])
def create_consultation():
    """Schedule a new AI stylist consultation"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ['date', 'focus_areas']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        consultation = StylistConsultation(
            user_id=user_id,
            date=data['date'],
            focus_areas=data['focus_areas'],
            questions=data.get('questions', []),
            style_preferences=data.get('style_preferences', {}),
            consultation_type=data.get('consultation_type', 'general')
        )
        
        consultation.save()
        
        return jsonify({
            "message": "Consultation scheduled successfully",
            "data": consultation.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error scheduling consultation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/stylist/consultations/<consultation_id>', methods=['GET'])
def get_consultation(consultation_id):
    """Get a specific consultation details"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    try:
        consultation = StylistConsultation.get_by_id(consultation_id)
        if not consultation:
            return jsonify({"error": "Consultation not found"}), 404
        
        # Only the consultation owner can view it
        if consultation.user_id != user_id:
            return jsonify({"error": "You don't have permission to view this consultation"}), 403
        
        return jsonify({
            "message": "Consultation retrieved successfully",
            "data": consultation.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving consultation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/stylist/generate-advice', methods=['POST'])
def generate_stylist_advice():
    """Generate AI stylist advice for specific questions or situations"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    if 'query' not in data:
        return jsonify({"error": "Missing required field: query"}), 400
    
    try:
        # TODO: Replace with actual Gemini API call
        # For now, we'll return mock data
        
        # Sample queries and responses
        sample_responses = {
            "casual office outfit": "For a casual office environment, I recommend pairing dark wash jeans with a crisp button-down shirt and loafers or ankle boots. Add a structured blazer for a more polished look. Keep accessories minimal with a simple watch and perhaps small stud earrings.",
            "date night outfit": "For a date night, consider a well-fitted dark pair of jeans or slacks with a silk or nice quality cotton top. Add a statement accessory like a bold necklace or interesting watch. Complete the look with a stylish jacket and comfortable but elegant shoes.",
            "wedding guest attire": "As a wedding guest, opt for a knee-length or midi dress in a festive color or pattern. For men, a suit in a color appropriate for the season is perfect. Avoid white or overly flashy outfits that might distract from the couple. Consider the venue and time of day - outdoor daytime weddings call for lighter colors, while evening affairs can be more formal."
        }
        
        # Default response for other queries
        default_response = "Based on current fashion trends and your style profile, I would recommend focusing on pieces that combine comfort with personal expression. Look for well-fitted basics in quality fabrics that can be layered and accessorized according to the occasion. Remember, the most stylish outfits are those where you feel confident and comfortable."
        
        # Get response based on query
        query_lower = data['query'].lower()
        response = None
        
        for key, value in sample_responses.items():
            if key in query_lower:
                response = value
                break
        
        if not response:
            response = default_response
        
        return jsonify({
            "message": "Stylist advice generated successfully",
            "data": {
                "query": data['query'],
                "advice": response,
                "generated_at": datetime.now().isoformat()
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error generating stylist advice: {str(e)}")
        return jsonify({"error": str(e)}), 500

#
# User Following Endpoints
#

@api_blueprint.route('/social/follow/<followed_id>', methods=['POST'])
def follow_user(followed_id):
    """Follow another user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    follower_id = payload.get('user_id') or payload.get('email')
    
    # Don't allow following yourself
    if follower_id == followed_id:
        return jsonify({"error": "You cannot follow yourself"}), 400
    
    try:
        # Check if already following
        existing = FollowRelationship.is_following(follower_id, followed_id)
        if existing:
            return jsonify({"error": "You are already following this user"}), 400
        
        # Create follow relationship
        follow = FollowRelationship(
            follower_id=follower_id,
            followed_id=followed_id
        )
        
        follow.save()
        
        return jsonify({
            "message": "You are now following this user"
        })
    except Exception as e:
        current_app.logger.error(f"Error following user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/unfollow/<followed_id>', methods=['POST'])
def unfollow_user(followed_id):
    """Unfollow a user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    follower_id = payload.get('user_id') or payload.get('email')
    
    try:
        # Check if following
        existing = FollowRelationship.is_following(follower_id, followed_id)
        if not existing:
            return jsonify({"error": "You are not following this user"}), 400
        
        # Remove follow relationship
        FollowRelationship.unfollow(follower_id, followed_id)
        
        return jsonify({
            "message": "You have unfollowed this user"
        })
    except Exception as e:
        current_app.logger.error(f"Error unfollowing user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/followers', methods=['GET'])
def get_followers():
    """Get users who follow the current user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    try:
        followers = FollowRelationship.get_followers(user_id)
        
        return jsonify({
            "message": "Followers retrieved successfully",
            "data": followers
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving followers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/social/following', methods=['GET'])
def get_following():
    """Get users the current user is following"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    try:
        following = FollowRelationship.get_following(user_id)
        
        return jsonify({
            "message": "Following list retrieved successfully",
            "data": following
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving following list: {str(e)}")
        return jsonify({"error": str(e)}), 500 