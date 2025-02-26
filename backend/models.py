from datetime import datetime

from sqlalchemy import Boolean, String, ForeignKey, TIMESTAMP, func, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: put an index on name
    name: Mapped[str] = mapped_column(String(30))
    is_agent: Mapped[bool] = mapped_column(
            Boolean,
            nullable=False,
            default=False)

    chat_messages = relationship("ChatMessage", back_populates="user")
    chats = relationship("Chat", back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r} is_agent={self.is_agent!r}"


class Chat(Base):
    """
    Represent a chat.

    Users owns chats. Chat participants are mapped to specific ChatMessage rows.
    Note: Multiple agents can participate in the same chat.
    Agents do not own chats.
    """
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    ts_added: Mapped[datetime] = mapped_column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now())

    user = relationship("User", back_populates="chats")
    messages = relationship("ChatMessage",
                            primaryjoin="ChatMessage.chat_id == Chat.id")

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, title={self.title!r}, user_id={self.user_id!r})"


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # TODO: put an index on ts_added
    ts_added: Mapped[datetime] = mapped_column(
            TIMESTAMP,
            nullable=False,
            server_default=func.now())

    user = relationship("User", back_populates="chat_messages")

