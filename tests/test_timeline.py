def test_timeline_is_chronological_and_keeps_unassigned():
    from domain.timeline import build_timeline
    rows=[{"trace_id":"2","occurred_at":"2026-01-01T10:00:00+00:00","event_type":"mail","work_item_id":None,"assignment_status":"unassigned","duration_seconds":10,"source":"mail"},{"trace_id":"1","occurred_at":"2026-01-01T09:00:00+00:00","event_type":"file","work_item_id":"W1","assignment_status":"confirmed","duration_seconds":20,"source":"file"}]
    entries=build_timeline(rows)
    assert [e.trace_id for e in entries] == ["1","2"]
    assert entries[1].work_item_id is None
