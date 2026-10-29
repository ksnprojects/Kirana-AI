"""Human-in-the-loop order draft manager; revalidates from source catalog before confirmation."""
from datetime import datetime,timezone
import copy,uuid
from core.catalog_matcher import CatalogMatcher,MatchResult

class OrderManager:
    def __init__(self,catalog_matcher:CatalogMatcher):
        self.catalog_matcher=catalog_matcher
        self.confirmed_orders_log=[]

    def create_empty_draft(self,store_id,store_name):
        return dict(draft_id='DRAFT-'+uuid.uuid4().hex[:8].upper(),store_id=store_id,store_name=store_name,
                    items=[],status='draft',can_confirm=False,grand_total_inr=0.0,total_base_units=0.0,
                    validation_errors=[],validation_warnings=[],created_at=datetime.now(timezone.utc).isoformat())

    def update_draft_with_items(self,draft,new_items,merge_mode='replace'):
        if draft.get('status')=='confirmed':
            raise ValueError('Cannot edit a confirmed order')
        prior=list(draft.get('items',[])) if merge_mode=='append' else []
        prior.extend([x.to_dict() if isinstance(x,MatchResult) else x for x in new_items])
        draft['items']=prior
        return self.recalculate_and_validate(draft)

    def resolve_ambiguity(self,draft,item_index,chosen_sku):
        items=draft['items']
        if not (0<=item_index<len(items)):raise IndexError('No such order line')
        item=items[item_index]
        authorized={c['sku'] for c in item.get('candidate_skus',[])}
        if item.get('status')!='ambiguous' or chosen_sku not in authorized:
            raise ValueError('Variant selection is not one of the valid catalog options')
        # Preserve the originally requested quantity and unit, including uncertainty.
        resolved=self.catalog_matcher.match_sku(chosen_sku,item.get('quantity'),item.get('unit'))
        items[item_index]=resolved.to_dict()
        return self.recalculate_and_validate(draft)

    def update_item_quantity(self,draft,item_index,new_quantity,new_unit=None):
        items=draft['items']
        if not (0<=item_index<len(items)):raise IndexError('No such order line')
        old=items[item_index]
        if old.get('sku') not in self.catalog_matcher.sku_lookup:
            raise ValueError('First select a valid product SKU')
        updated=self.catalog_matcher.match_sku(old['sku'],new_quantity,new_unit if new_unit is not None else old.get('unit'))
        items[item_index]=updated.to_dict()
        return self.recalculate_and_validate(draft)

    def remove_item(self,draft,item_index):
        if not (0<=item_index<len(draft['items'])):raise IndexError('No such order line')
        draft['items'].pop(item_index)
        return self.recalculate_and_validate(draft)

    def add_nudge_item(self,draft,sku,quantity,unit='pack'):
        match=self.catalog_matcher.match_sku(sku,quantity,unit)
        if match.status!='matched':
            raise ValueError('A proposed nudge is not a valid available product/order unit')
        return self.update_draft_with_items(draft,[match],merge_mode='append')

    def recalculate_and_validate(self,draft):
        errors=[];warnings=[];new_items=[];total=0.;unit_count=0
        if not draft.get('items'):errors.append('Order is empty.')
        for idx,item in enumerate(draft.get('items',[]),1):
            # CRITICAL: never trust prices/totals or matched statuses from earlier cached output.
            sku=item.get('sku'); status=item.get('status')
            if status=='ambiguous':
                errors.append(f'Line {idx}: Select an exact catalog variant.');new_items.append(item);continue
            if status=='unknown_product' or not sku:
                errors.append(f'Line {idx}: Unknown product; remove or review.');new_items.append(item);continue
            canonical=self.catalog_matcher.match_sku(sku,item.get('quantity'),item.get('unit'),item.get('raw_product_mention'))
            clean=canonical.to_dict();new_items.append(clean)
            if canonical.status!='matched':
                errors.append(f'Line {idx}: {canonical.clarification_message or canonical.status}')
            else:
                total+=canonical.line_total_inr;unit_count+=canonical.base_quantity
        draft['items']=new_items
        draft['grand_total_inr']=round(total,2)
        draft['total_base_units']=unit_count
        draft['validation_errors']=errors
        draft['validation_warnings']=warnings
        draft['can_confirm']=not errors and bool(new_items)
        draft['status']='ready_for_confirmation' if draft['can_confirm'] else 'awaiting_clarification' if any(x.get('status') in ('ambiguous','needs_clarification') for x in new_items) else 'draft'
        return draft

    def confirm_order(self,draft):
        # Confirmation must re-check availability, quantity and prices at time of click.
        if draft.get('status')=='confirmed':return None
        self.recalculate_and_validate(draft)
        if not draft.get('can_confirm'):return None
        confirmed=dict(order_id='ORD-'+uuid.uuid4().hex[:10].upper(),draft_id=draft['draft_id'],
            store_id=draft['store_id'],store_name=draft['store_name'],
            items_detail=copy.deepcopy(draft['items']),items_count=len(draft['items']),
            total_base_units=draft['total_base_units'],grand_total_inr=draft['grand_total_inr'],
            confirmation_timestamp=datetime.now(timezone.utc).isoformat(),status='Confirmed (Simulated)',
            dispatch_simulation_notice='Academic prototype only; no warehouse or payment integration.')
        draft['status']='confirmed';draft['can_confirm']=False
        self.confirmed_orders_log.insert(0,confirmed)
        return confirmed
