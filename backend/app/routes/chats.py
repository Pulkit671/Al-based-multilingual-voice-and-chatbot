from bson import ObjectId
from deep_translator import GoogleTranslator
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.config import get_settings
from app.database import get_database
from app.models import serialize_document, utc_now
from app.schemas.chat import ChatCreateRequest, ChatDetailResponse, ChatSummaryResponse, MessageCreateRequest, MessageResponse
from app.services.medical_chat_service import build_assistant_response
from app.utils.auth import get_current_user
from app.utils.translator import translator_service

router = APIRouter(prefix='/chats', tags=['Chats'])
settings = get_settings()

LANGUAGE_MAP = {
    'en': 'en',
    'hi': 'hi',
    'mr': 'mr',
    'bn': 'bn',
    'ta': 'ta',
    'te': 'te',
    'fr': 'fr',
    'es': 'es',
    'de': 'de',
    'ar': 'ar',
    'zh-cn': 'zh-CN',
    'zh-CN': 'zh-CN',
    'ja': 'ja',
}


def _ensure_chat_owner(db: Database, chat_id: str, user_id: str):
    if not ObjectId.is_valid(chat_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')
    chat = db.chats.find_one({'_id': ObjectId(chat_id), 'user_id': ObjectId(user_id)})
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')
    return chat


def _translate_to_english(text: str, language: str) -> str:
    if language == 'en':
        return text
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as exc:
        print(f'Input translation failed ({language} -> en): {exc}')
        return text


def _translate_from_english(text: str, language: str) -> str:
    if language == 'en':
        return text
    try:
        return GoogleTranslator(source='en', target=language).translate(text)
    except Exception as exc:
        print(f'Output translation failed (en -> {language}): {exc}')
        return text


@router.post('/new', response_model=ChatSummaryResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    payload: ChatCreateRequest,
    current_user=Depends(get_current_user),
    db: Database = Depends(get_database),
):
    now = utc_now()
    chat_document = {
        'user_id': ObjectId(current_user['id']),
        'title': payload.title.strip() if payload.title else 'New Medical Chat',
        'created_at': now,
        'updated_at': now,
    }
    result = db.chats.insert_one(chat_document)
    created_chat = db.chats.find_one({'_id': result.inserted_id})
    serialized_chat = serialize_document(created_chat)
    serialized_chat['last_message'] = None
    return ChatSummaryResponse(**serialized_chat)


@router.get('/', response_model=list[ChatSummaryResponse])
def list_chats(current_user=Depends(get_current_user), db: Database = Depends(get_database)):
    chats = list(db.chats.find({'user_id': ObjectId(current_user['id'])}).sort('updated_at', -1))
    chat_ids = [chat['_id'] for chat in chats]
    latest_messages_map = {}

    if chat_ids:
        pipeline = [
            {'$match': {'chat_id': {'$in': chat_ids}}},
            {'$sort': {'created_at': -1}},
            {'$group': {'_id': '$chat_id', 'text': {'$first': '$text'}}},
        ]
        for item in db.messages.aggregate(pipeline):
            latest_messages_map[str(item['_id'])] = item.get('text')

    response = []
    for chat in chats:
        serialized = serialize_document(chat)
        serialized['last_message'] = latest_messages_map.get(serialized['id'])
        if not serialized['last_message']:
            continue
        response.append(ChatSummaryResponse(**serialized))
    return response


@router.get('/{chat_id}', response_model=ChatDetailResponse)
def get_chat(chat_id: str, current_user=Depends(get_current_user), db: Database = Depends(get_database)):
    chat = _ensure_chat_owner(db, chat_id, current_user['id'])
    messages = list(db.messages.find({'chat_id': ObjectId(chat_id)}).sort('created_at', 1))
    serialized_chat = serialize_document(chat)
    serialized_messages = [MessageResponse(**serialize_document(message)) for message in messages]
    return ChatDetailResponse(**serialized_chat, messages=serialized_messages)


@router.delete('/{chat_id}')
def delete_chat(chat_id: str, current_user=Depends(get_current_user), db: Database = Depends(get_database)):
    _ensure_chat_owner(db, chat_id, current_user['id'])
    object_chat_id = ObjectId(chat_id)
    db.messages.delete_many({'chat_id': object_chat_id, 'user_id': ObjectId(current_user['id'])})
    db.chats.delete_one({'_id': object_chat_id, 'user_id': ObjectId(current_user['id'])})
    return {'success': True, 'message': 'Chat deleted successfully'}


@router.post('/{chat_id}/message')
def send_message(
    chat_id: str,
    payload: MessageCreateRequest,
    current_user=Depends(get_current_user),
    db: Database = Depends(get_database),
):
    chat = _ensure_chat_owner(db, chat_id, current_user['id'])
    normalized_language = translator_service.normalize_language(payload.language or current_user.get('preferred_language'))
    selected_language = LANGUAGE_MAP.get(normalized_language, 'en')
    now = utc_now()

    user_message = {
        'chat_id': ObjectId(chat_id),
        'user_id': ObjectId(current_user['id']),
        'role': 'user',
        'text': payload.text.strip(),
        'language': selected_language,
        'voice_path': None,
        'created_at': now,
    }
    user_message_result = db.messages.insert_one(user_message)

    new_title = chat.get('title', 'New Medical Chat')
    if new_title == 'New Medical Chat':
        new_title = payload.text.strip()[:50]

    db.chats.update_one(
        {'_id': ObjectId(chat_id)},
        {'$set': {'title': new_title, 'updated_at': utc_now()}},
    )

    model_input_text = _translate_to_english(payload.text.strip(), selected_language)
    print('Language:', selected_language)
    print('Input:', model_input_text)

    pipeline_result = build_assistant_response(model_input_text)
    response_text = _translate_from_english(pipeline_result['response_text'], selected_language)
    print('Output:', response_text)

    assistant_message = {
        'chat_id': ObjectId(chat_id),
        'user_id': ObjectId(current_user['id']),
        'role': 'assistant',
        'text': response_text,
        'language': selected_language,
        'voice_path': None,
        'created_at': utc_now(),
    }
    assistant_message_result = db.messages.insert_one(assistant_message)

    db.users.update_one(
        {'_id': ObjectId(current_user['id'])},
        {'$set': {'preferred_language': selected_language}},
    )

    saved_user = db.messages.find_one({'_id': user_message_result.inserted_id})
    saved_assistant = db.messages.find_one({'_id': assistant_message_result.inserted_id})

    return {
        'user_message': MessageResponse(**serialize_document(saved_user)),
        'assistant_message': MessageResponse(**serialize_document(saved_assistant)),
    }
