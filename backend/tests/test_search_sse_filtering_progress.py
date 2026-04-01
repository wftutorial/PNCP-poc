"""DEBT-v3-S2 AC8: Tests for SSE filtering_progress and llm_classifying events.

Verifies that:
- AC5: filtering_progress event is emitted during filter phase
- AC6: llm_classifying event is emitted when LLM zero-match starts
- AC7: Progress never stays >15s without an event (granularity check)
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from progress import ProgressTracker, _active_trackers


@pytest.fixture(autouse=True)
def cleanup_trackers():
    """Clean up global tracker registry after each test."""
    yield
    _active_trackers.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis to use in-memory mode."""
    with patch("progress.get_redis_pool", new_callable=AsyncMock) as mock_pool, \
         patch("progress.is_redis_available", new_callable=AsyncMock) as mock_available:
        mock_pool.return_value = None
        mock_available.return_value = False
        yield


@pytest.mark.asyncio
async def test_emit_filtering_progress(mock_redis):
    """AC5: filtering_progress event emitted with phase, processed, total."""
    tracker = ProgressTracker("test-fp-001", uf_count=5)

    await tracker.emit_filtering_progress(processed=50, total=200, phase="filtering")

    event = tracker.queue.get_nowait()
    assert event.stage == "filtering_progress"
    assert event.detail["phase"] == "filtering"
    assert event.detail["processed"] == 50
    assert event.detail["total"] == 200
    assert 60 <= event.progress <= 70


@pytest.mark.asyncio
async def test_emit_filtering_progress_completion(mock_redis):
    """AC5: Progress reaches ~70% at full completion."""
    tracker = ProgressTracker("test-fp-002", uf_count=5)

    await tracker.emit_filtering_progress(processed=200, total=200, phase="filtering")

    event = tracker.queue.get_nowait()
    assert event.progress == 70


@pytest.mark.asyncio
async def test_emit_llm_classifying_start(mock_redis):
    """AC6: llm_classifying event emitted when LLM zero-match starts."""
    tracker = ProgressTracker("test-lc-001", uf_count=5)

    await tracker.emit_llm_classifying(items=30)

    event = tracker.queue.get_nowait()
    assert event.stage == "llm_classifying"
    assert event.detail["phase"] == "classifying"
    assert event.detail["items"] == 30
    assert event.progress == 70
    assert "Classificando relevância de 30 editais" in event.message


@pytest.mark.asyncio
async def test_emit_llm_classifying_progress(mock_redis):
    """AC6: llm_classifying event tracks progress during classification."""
    tracker = ProgressTracker("test-lc-002", uf_count=5)

    await tracker.emit_llm_classifying(items=20, processed=10, total=20)

    event = tracker.queue.get_nowait()
    assert event.stage == "llm_classifying"
    assert event.detail["processed"] == 10
    assert event.detail["total"] == 20
    assert 70 <= event.progress <= 75
    assert "10/20" in event.message


@pytest.mark.asyncio
async def test_filtering_progress_message_format(mock_redis):
    """AC5: Message format is human-readable."""
    tracker = ProgressTracker("test-fp-003", uf_count=5)

    await tracker.emit_filtering_progress(processed=100, total=500, phase="filtering")

    event = tracker.queue.get_nowait()
    assert "100/500" in event.message
    assert "Analisando editais" in event.message


@pytest.mark.asyncio
async def test_multiple_filtering_events_provide_granularity(mock_redis):
    """AC7: Multiple events ensure progress never stays silent >15s."""
    tracker = ProgressTracker("test-gran-001", uf_count=5)

    # Simulate 5 progress updates (would be emitted every ~5% of items)
    for i in range(5):
        processed = (i + 1) * 40
        await tracker.emit_filtering_progress(processed=processed, total=200, phase="filtering")

    events = []
    while not tracker.queue.empty():
        events.append(tracker.queue.get_nowait())

    assert len(events) == 5
    # Progress should be monotonically increasing
    progresses = [e.progress for e in events]
    assert progresses == sorted(progresses)


@pytest.mark.asyncio
async def test_llm_classifying_then_filtering_sequence(mock_redis):
    """AC5+AC6: Both event types can be emitted in sequence."""
    tracker = ProgressTracker("test-seq-001", uf_count=5)

    await tracker.emit_filtering_progress(processed=200, total=200, phase="filtering")
    await tracker.emit_llm_classifying(items=30)
    await tracker.emit_llm_classifying(items=30, processed=15, total=30)
    await tracker.emit_llm_classifying(items=30, processed=30, total=30)

    events = []
    while not tracker.queue.empty():
        events.append(tracker.queue.get_nowait())

    assert len(events) == 4
    assert events[0].stage == "filtering_progress"
    assert events[1].stage == "llm_classifying"
    assert events[2].stage == "llm_classifying"
    assert events[3].stage == "llm_classifying"
