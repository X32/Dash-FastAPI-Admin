from fastapi import HTTPException, status


class ConversationException(HTTPException):
    """会话管理基础异常类"""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class ConversationNotFoundException(ConversationException):
    """会话不存在异常"""
    
    def __init__(self, detail: str = "会话不存在"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class MessageNotFoundException(ConversationException):
    """消息不存在异常"""
    
    def __init__(self, detail: str = "消息不存在"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UserPermissionException(ConversationException):
    """用户权限异常"""
    
    def __init__(self, detail: str = "无权限访问该资源"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class InvalidParameterException(ConversationException):
    """参数校验异常"""
    
    def __init__(self, detail: str = "参数不合法"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class DatabaseException(ConversationException):
    """数据库操作异常"""
    
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessageContentNotFoundException(ConversationException):
    """消息内容不存在异常"""
    
    def __init__(self, detail: str = "消息内容不存在"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class PermissionDeniedException(ConversationException):
    """权限拒绝异常"""
    
    def __init__(self, detail: str = "权限被拒绝"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class InvalidConversationDataException(ConversationException):
    """会话数据无效异常"""
    
    def __init__(self, detail: str = "会话数据无效"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidMessageDataException(ConversationException):
    """消息数据无效异常"""
    
    def __init__(self, detail: str = "消息数据无效"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)