"""Mocked test: HTTP 404 from first model retries newer model; other errors do not."""
from unittest.mock import Mock
from types import SimpleNamespace
import core.llm_service as llm_module
import config
from core.llm_service import LLMService

class ApiError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(f'HTTP {code}')

def _service():
    svc=LLMService(catalog_matcher=Mock())
    svc.client=Mock()
    return svc

def test_404_retries_modern_model(monkeypatch):
    svc=_service()
    monkeypatch.setattr(llm_module, "types", SimpleNamespace(GenerateContentConfig=lambda **kw:kw), raising=False)
    monkeypatch.setattr(config,'DEFAULT_GEMINI_MODEL','gemini-3.5-flash-lite')
    monkeypatch.setattr(config,'GEMINI_404_FALLBACK_MODEL','gemini-3.8-flash')
    svc.catalog_matcher.retrieve_catalog_context.return_value=[]
    svc.client.models.generate_content.side_effect=[ApiError(404),Mock(text='{"intent":"order","items":[]}')]
    parsed=svc._call_gemini('2 packets Maggi')
    assert parsed.intent=='order'
    assert svc.last_successful_model=='gemini-3.8-flash'
    calls=svc.client.models.generate_content.call_args_list
    assert [c.kwargs['model'] for c in calls]==['gemini-3.5-flash-lite','gemini-3.8-flash']

def test_403_not_retried(monkeypatch):
    svc=_service()
    monkeypatch.setattr(llm_module, "types", SimpleNamespace(GenerateContentConfig=lambda **kw:kw), raising=False)
    monkeypatch.setattr(config,'DEFAULT_GEMINI_MODEL','gemini-3.5-flash-lite')
    monkeypatch.setattr(config,'GEMINI_404_FALLBACK_MODEL','gemini-3.8-flash')
    svc.catalog_matcher.retrieve_catalog_context.return_value=[]
    svc.client.models.generate_content.side_effect=ApiError(403)
    try:
        svc._call_gemini('2 packets Maggi')
    except ApiError as e:
        assert e.code==403
    else:
        raise AssertionError('Expected API error')
    assert svc.client.models.generate_content.call_count==1
