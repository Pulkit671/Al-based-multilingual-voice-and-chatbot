import MessageBubble from './MessageBubble'

export default function ChatWindow({ chat, loading, sending }) {
  const messages = chat?.messages || []
  const isEmpty = !loading && !sending && messages.length === 0

  return (
    <section className={`chat-window ${isEmpty ? 'empty' : ''}`}>
      <div className="messages-stack">
        {loading ? <div className="typing-indicator">Loading messages...</div> : null}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {sending ? <div className="typing-indicator">MedAI is preparing a response...</div> : null}
      </div>
    </section>
  )
}
