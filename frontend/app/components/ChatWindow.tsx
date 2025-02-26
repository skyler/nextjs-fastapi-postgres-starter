"use client";

import { useEffect, useState } from "react";

const wsURL = "ws://localhost:8000/chat";

interface ChatMessage {
  user: string;
  text: string;
}

interface ChatWindowProps {
  user: string;
  messageHistory: ChatMessage[];
}

export default function ChatWindow({ user, messageHistory }: ChatWindowProps) {
  const hist: ChatMessages[] = messageHistory as ChatMessage[];
  console.log("history", messageHistory);

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<ChatMessage[]>(hist);
  const [input, setInput] = useState("");

  useEffect(() => {
    const ws = new WebSocket(wsURL);

    ws.onopen = () => {
      console.log("Connected to websocket");
      setSocket(ws);
      setConnected(true);
    };

    ws.onmessage = (event) => {
      console.log("Got message raw:", event.data);
      const message = JSON.parse(event.data) as ChatMessage;
      setMessages(prevMessages => [...prevMessages, message]);
    };

    ws.onclose = () => {
      console.log("Websocket connection closed");
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (socket && input.trim()) {

      const message: ChatMessage = {
        user: user,
        text: input,
      }

      setMessages([...messages, message]);
      socket.send(JSON.stringify(message));
      setInput("");
    }
  };

  return (
    <div className="fixed bottom-4 right-4 w-96 p-4 border rounded shadow-md bg-white">
      {/* TODO: receive the agent name as a special message type.
        And set the title to "Connected to ${agent}" */}
      <h2 className="text-xl mb-2">Chat with Support</h2>
      <div className="h-64 overflow-y-auto mb-4 border p-2 rounded bg-gray-100">
        {messages.map((msg, index) => (
            <div key={index} className={`mb-2 ${msg.user == user ? 'text-left' : 'text-right'}`}>
              <div className="text-xs text-gray-500 mt-1">
                {msg.user}
              </div>
              <span className={`inline-block p-2 rounded-lg ${msg.user == user ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                {msg.text}
              </span>
            </div>
          ))}
      </div>
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-grow mr-2 p-2 border border-gray-300 rounded"
            placeholder="Type a message..."
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            disabled={!isConnected}
          >
          Send
          </button>
        </form>
    </div>
  );
}
