function formatDate(value) {
  return new Date(value).toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
  })
}

export default function Sidebar({ chats, activeChatId, onSelectChat, onCreateChat, onDeleteChat, loading }) {
  const handleDelete = (event, chat) => {
    event.stopPropagation()
    if (window.confirm(`Delete "${chat.title}" and all its messages?`)) {
      onDeleteChat(chat.id)
    }
  }

  return (
    <aside className="sidebar">
      <button type="button" className="primary-button new-chat-button" onClick={onCreateChat}>
        + New Chat
      </button>

      <div className="sidebar-list">
        {loading ? (
          <p className="sidebar-empty">Loading conversations...</p>
        ) : chats.length === 0 ? (
          <p className="sidebar-empty">Start a new chat to save medical conversations here.</p>
        ) : (
          chats.map((chat) => (
            <button
              type="button"
              key={chat.id}
              className={`chat-card ${activeChatId === chat.id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat.id)}
            >
              <div>
                <strong>{chat.title}</strong>
                <p>{chat.last_message || 'No messages yet'}</p>
              </div>
              <div className="chat-card-footer">
                <span>{formatDate(chat.updated_at)}</span>
                <span
                  role="button"
                  tabIndex={0}
                  className="delete-chat-button"
                  onClick={(event) => handleDelete(event, chat)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      handleDelete(event, chat)
                    }
                  }}
                >
                  Delete
                </span>
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  )
}
