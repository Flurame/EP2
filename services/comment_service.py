from database import db
from datetime import datetime

class CommentService:
    @staticmethod
    def create_comment(message, master_id, request_id):
        try:
            from models.comment import Comment
            new_comment = Comment(message=message, master_id=master_id, request_id=request_id, created_at=datetime.utcnow())
            db.session.add(new_comment)
            db.session.commit()
            return new_comment.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def get_comment_by_id(comment_id):
        try:
            from models.comment import Comment
            comment = Comment.query.get(comment_id)
            if not comment:
                return None
            return comment.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_comments_by_request(request_id):
        try:
            from models.comment import Comment
            comments = Comment.query.filter_by(request_id=request_id).all()
            return [c.to_dict() for c in comments]
        except Exception as e:
            return {'error': str(e)}
