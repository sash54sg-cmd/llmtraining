import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace

from src.api.main import app


class DummyDB:
    def add(self, obj):
        pass

    def commit(self):
        pass


class FakeAI:
    def generate_response(self, user_message, context=None, image_analysis=None, transcription=None):
        parts = ["FAKE_RESPONSE"]
        if image_analysis:
            parts.append("IMAGE_OK")
        if transcription:
            parts.append("TRANS_OK")
        return " | ".join(parts)


class FakeFoodModel:
    def predict(self, img_path):
        return [{"food_name": "Test Food", "confidence_percent": 92.5}]

    def estimate_portion_size(self, img_path):
        return {"portion_size": "medium", "portion_multiplier": 1.0}


class FakeImageHandler:
    def save_uploaded_image(self, data, filename, user_id):
        # write to temp file
        path = f"tests/tmp_{user_id}.jpg"
        with open(path, 'wb') as f:
            f.write(data)
        return path


class FakeAudioHandler:
    def save_audio(self, data, filename, user_id):
        path = f"tests/tmp_audio_{user_id}.wav"
        with open(path, 'wb') as f:
            f.write(data)
        return path

    def transcribe(self, path):
        return "hello from audio"


def test_multimodal_text_only(monkeypatch):
    # Override auth and db dependencies
    fake_user = SimpleNamespace(id=1, profile=SimpleNamespace(goal_type='weight_loss', dietary_type='omnivore', target_calories=2000))
    from src.api.auth import get_current_active_user
    from src.config.database import get_db

    app.dependency_overrides[get_current_active_user] = lambda: fake_user
    app.dependency_overrides[get_db] = lambda: DummyDB()

    # Monkeypatch heavy models and handlers
    import src.api.routes.chat_routes as chat_routes
    monkeypatch.setattr(chat_routes, 'get_conversational_ai', lambda: FakeAI())
    monkeypatch.setattr(chat_routes, 'get_image_handler', lambda: FakeImageHandler())
    monkeypatch.setattr(chat_routes, 'get_food_model', lambda: FakeFoodModel())
    monkeypatch.setattr(chat_routes, 'get_audio_handler', lambda: FakeAudioHandler())

    with TestClient(app) as client:
        resp = client.post('/api/chat/multimodal', data={'message': 'Hello AI'})
        assert resp.status_code == 200
        body = resp.json()
        assert 'response' in body
        assert 'FAKE_RESPONSE' in body['response']


def test_multimodal_image_and_audio(monkeypatch):
    fake_user = SimpleNamespace(id=2, profile=SimpleNamespace(goal_type='maintain', dietary_type='vegan', target_calories=1800))
    from src.api.auth import get_current_active_user
    from src.config.database import get_db

    app.dependency_overrides[get_current_active_user] = lambda: fake_user
    app.dependency_overrides[get_db] = lambda: DummyDB()

    import src.api.routes.chat_routes as chat_routes
    monkeypatch.setattr('src.ai.conversational_ai.get_conversational_ai', lambda: FakeAI())
    monkeypatch.setattr(chat_routes, 'get_image_handler', lambda: FakeImageHandler())
    monkeypatch.setattr(chat_routes, 'get_food_model', lambda: FakeFoodModel())
    monkeypatch.setattr(chat_routes, 'get_audio_handler', lambda: FakeAudioHandler())

    # create small fake files
    img_bytes = b"\xFF\xD8\xFF\xE0" + b"0" * 100  # not a valid image but enough bytes
    audio_bytes = b"RIFF" + b"0" * 200

    files = {
        'file': ('photo.jpg', img_bytes, 'image/jpeg')
    }

    with TestClient(app) as client:
        resp = client.post('/api/chat/multimodal', data={'message': 'See this'}, files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert 'image_analysis' in body
        assert body['image_analysis']['predictions'][0]['food_name'] == 'Test Food'

    files_audio = {
        'file': ('note.wav', audio_bytes, 'audio/wav')
    }

    with TestClient(app) as client:
        resp = client.post('/api/chat/multimodal', files=files_audio)
        assert resp.status_code == 200
        body = resp.json()
        assert 'transcription' in body
        assert body['transcription'] == 'hello from audio'