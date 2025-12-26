from flask import Blueprint, request, jsonify
from database import db

comments_bp = Blueprint('comments', __name__, url_prefix='/api/comments')

@comments_bp.route('/', methods=['POST'])
def create_comment():
    from models.comment import Comment
    data = request.get_json()
    required_fields = ['message', 'master_id', 'request_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        new_comment = Comment(
            message=data['message'],
            master_id=data['master_id'],
            request_id=data['request_id']
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify(new_comment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@comments_bp.route('/request/<int:request_id>', methods=['GET'])
def get_comments_for_request(request_id):
    from models.comment import Comment
    try:
        comments = Comment.query.filter_by(request_id=request_id).all()
        return jsonify([c.to_dict() for c in comments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@comments_bp.route('/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    from models.comment import Comment
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        return jsonify(comment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
