from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from pydantic import BaseModel, computed_field, Field
from typing import List

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from seed import seed_user_if_needed
from db_engine import engine
from models import User, Chat, ChatMessage

from wonderwords import RandomSentence

import logging
import json

logging.getLogger().setLevel("INFO")

seed_user_if_needed()

app = FastAPI()


class UserRead(BaseModel):
    id: int
    name: str


class SocketMessage(BaseModel):
    user: str
    text: str


class ChatMessageRead(BaseModel):
    text: str
    user: str


@app.get("/users/me")
async def get_my_user():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Sample logic to simplify getting the current user. There's only one user.
            result = await session.execute(select(User))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(id=user.id, name=user.name)


@app.get("/chats/{user}")
async def get_user_chats(user: str):
    """
    Load the most recent chats for initial display.
    """
    stmt = (
        select(ChatMessage)
        .join(Chat)
        .join(User, User.id == Chat.user_id)
        .where(User.name == user)
        .limit(100)
        .options(
            selectinload(ChatMessage.user)
        )
    )
    res = []
    async with AsyncSession(engine) as session:
        result = await session.execute(stmt)
        for msg in result.scalars().all():
            #logging.info("history belongs to user: %s", msg.chat
            res.append(ChatMessageRead(user=msg.user.name, text=msg.text))

    logging.info("Loaded %d chat histories for %s", len(res), user)
    return res


@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    logging.info("Got websocket connection")

    chat_id = None
    agent_id = None
    agent_name = None
    user_id = None

    async with AsyncSession(engine) as session:
        async with session.begin():
            # TODO: use a session to track the current user.
            result = await session.execute(select(User))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            user_id = user.id

            stmt = select(User).where(
                    User.is_agent == True).order_by(func.random()).limit(1)
            result = await session.execute(stmt)
            agent = result.scalars().first()
            if agent is None:
                raise HTTPException(status_code=404, detail="Agent not found")

            agent_id = agent.id
            agent_name = agent.name

            chat = Chat(user_id=user.id)
            session.add(chat)
            await session.flush()
            chat_id = chat.id

    logging.info(f"Selected agent {agent_name} for chat id: {chat_id}")

    while True:
        try:
            raw  = await websocket.receive_text()
        except WebSocketDisconnect:
            websocket.close()
            break

        data = json.loads(raw)
        socket_msg = SocketMessage(**data)
        
        logging.info(f"Got websocket data: {raw}")

        wonder = RandomSentence()
        generated = wonder.simple_sentence()

        async with AsyncSession(engine) as session:
            async with session.begin():
                # The message we received.
                message_in = ChatMessage(
                        chat_id=chat_id,
                        user_id=user_id,
                        text=socket_msg.text)
                session.add(message_in)

                # The message we're sending.
                message_out = ChatMessage(
                        chat_id=chat_id,
                        user_id=agent_id,
                        text=generated)
                session.add(message_out)
                await session.flush()

        new_message = SocketMessage(user=agent_name, text=generated).json()
        await websocket.send_text(new_message)
