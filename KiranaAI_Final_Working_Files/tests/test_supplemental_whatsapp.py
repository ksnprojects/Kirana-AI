import json
from core.data_loader import DataLoader


def test_combined_whatsapp_corpus():
    loader = DataLoader()
    df = loader.get_whatsapp_orders()
    assert len(df) == 340
    assert df.message_id.is_unique
    assert df.raw_message.notna().all()
    assert set(df.store_id).issubset(set(loader.get_store_master().store_id))
    external = df[df.message_id.str.startswith('EXT_')]
    assert len(external) == 300
    assert not external.evaluation_eligible.fillna(False).any()
    assert external.source_ground_truth_json.map(lambda s: isinstance(json.loads(s or '[]'), list)).all()
    assert len(loader.get_evaluation_cases()) == 40
    assert len(loader.get_catalog()) == 40
