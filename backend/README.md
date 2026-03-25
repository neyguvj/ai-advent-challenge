# AI Assistant Backend

This is the backend service for an AI assistant that handles user sessions and message history.

## API Endpoints

### Message History Endpoints

#### Append a new message to a session
```
POST /api/sessions/{session_id}/messages
```

**Request Body:**
```json
{
  "role": "system|assistent|user",
  "content": "Message content"
}
```

**Response:**
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "timestamp": "datetime",
  "role": "system|assistent|user",
  "content": "Message content"
}
```

#### Get all messages for a session
```
GET /api/sessions/{session_id}/messages
```

**Response:**
```json
[
  {
    "id": "uuid",
    "session_id": "uuid",
    "timestamp": "datetime",
    "role": "system|assistent|user",
    "content": "Message content"
  },
]
```

#### Delete all messages for a session
```
DELETE /api/sessions/{session_id}/messages
```

**Response:**
```json
{
  "message": "Successfully deleted X messages",
  "count": "X"
}
```

#### Append multiple messages to a session (batch)
```
POST /api/sessions/{session_id}/messages/batch
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "system|assistent|user",
      "content": "Message content 1"
    },
    {
      "role": "system|assistent|user",
      "content": "Message content 2"
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "session_id": "uuid",
    "timestamp": "datetime",
    "role": "system|assistent|user",
    "content": "Message content 1"
  },
]
```