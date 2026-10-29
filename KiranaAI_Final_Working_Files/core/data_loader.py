"""Load original catalog and internally consistent simulated datasets."""
import pandas as pd
import streamlit as st
import config

class DataLoader:
    def __init__(self):
        self._cache = {}

    def _read(self, name, path):
        if name not in self._cache:
            self._cache[name] = pd.read_csv(path)
        return self._cache[name]

    def get_catalog(self):
        df = self._read('catalog', config.CATALOG_FILE)
        assert len(df) == 40 and df.sku_id.is_unique, '40-SKU source catalog is required'
        return df

    def get_catalog_processed(self):
        return self._read('catalog_processed', config.CATALOG_PROCESSED_FILE)

    def get_store_master(self):
        df = self._read('stores', config.STORE_MASTER_FILE)
        assert len(df) == 30 and df.store_id.is_unique
        return df

    def get_store_history(self):
        return self._read('history', config.STORE_HISTORY_FILE)

    def get_reorder_dataset(self):
        return self._read('reorder', config.REORDER_DATASET_FILE)

    def get_whatsapp_orders(self):
        """Return the original 40 labelled cases plus 300 supplemental text examples.

        Supplemental source labels use another 20-SKU catalog and are explicitly
        NOT held-out 40-SKU benchmark ground truth. The dashboard remains unchanged.
        """
        if 'whatsapp_combined' not in self._cache:
            from pathlib import Path
            original = self._read('whatsapp', config.WHATSAPP_ORDERS_FILE).copy()
            original['supplemental_source'] = 'original_40sku_labelled_dataset'
            original['evaluation_eligible'] = True
            original['validation_status'] = '40sku_labelled'
            supplemental_path = Path(config.CATALOG_FILE).parent / 'supplemental_whatsapp_orders_300.csv'
            if supplemental_path.exists():
                supplemental = self._read('whatsapp_supplemental', supplemental_path)
                self._cache['whatsapp_combined'] = pd.concat([original, supplemental], ignore_index=True, sort=False)
            else:
                self._cache['whatsapp_combined'] = original
        return self._cache['whatsapp_combined']

    def get_evaluation_cases(self):
        return self._read('evaluation_cases', config.EVALUATION_CASES_FILE)

    def get_edge_cases(self):
        return self._read('edge_cases', config.EDGE_CASES_FILE)

    def load_all(self):
        catalog = self.get_catalog()
        stores = self.get_store_master()
        history = self.get_store_history()
        feat = self.get_reorder_dataset()
        msgs = self.get_whatsapp_orders()
        assert set(history.sku_id).issubset(set(catalog.sku_id))
        assert set(history.store_id).issubset(set(stores.store_id))
        assert set(feat.sku_id).issubset(set(catalog.sku_id))
        assert set(feat.store_id).issubset(set(stores.store_id))
        assert set(msgs.store_id).issubset(set(stores.store_id))
        return dict(catalog=catalog,stores=stores,history=history,reorder=feat,whatsapp=msgs)

    def get_store_info(self, store_id):
        found = self.get_store_master().query('store_id == @store_id')
        return found.iloc[0].to_dict() if len(found) else None

@st.cache_resource
def get_data_loader():
    loader = DataLoader()
    loader.load_all()
    return loader
