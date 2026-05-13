export default function MessageBubble({ message }) {
  const isAssistant = message.role === 'assistant'
  const sentAt = message.created_at ? new Date(message.created_at) : new Date()

  return (
    <article className={`message-row ${isAssistant ? 'assistant' : 'user'}`}>
      <div className={`message-bubble ${isAssistant ? 'assistant' : 'user'}`}>
        <div className="message-meta">
          <span>{isAssistant ? 'MedAI' : 'You'}</span>
          <small>{sentAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
        </div>

        {message.text ? <p className="message-text">{message.text}</p> : null}
      </div>
    </article>
  )
}
