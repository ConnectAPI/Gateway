from uuid import uuid4
from middleware_core import BaseMiddleware
from models.request import Request
from models.service import Service
from datetime import datetime


class SessionLoggerMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, service: Service):
        session_id = request.session.get("session_id")
        if session_id is None:
            session_id = str(uuid4())
            request.session["session_id"] = session_id
        self.context.cache.set_item(f"{session_id}_session_last_message", datetime.utcnow().timestamp())
        return await self.next(request, service)
