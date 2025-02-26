import Image from "next/image";
import ChatWindow from "./components/ChatWindow";

type User = {
  id: string;
  name: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

export default async function Home() {
  // Fetch the current user.
  console.log("fetch", `${apiUrl}/users/me`);
  const user: User = await fetch(`${apiUrl}/users/me`).then((res) =>
    res.json()
  );

  // Fetch the current user's chat history.
  console.log("fetching chat history for", user.name);
  const messageHistory = await fetch(`${apiUrl}/chats/${user.name}`).then((res) =>
    res.json()
  );

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <p>Hello, {user.name}!</p>
      <ChatWindow user={user.name} messageHistory={messageHistory} />
    </main>
  );
}
