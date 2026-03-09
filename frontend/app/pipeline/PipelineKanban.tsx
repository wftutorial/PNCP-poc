"use client";

import { useState, useCallback, useEffect } from "react";
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { STAGES_ORDER, type PipelineItem, type PipelineStage } from "./types";
import { PipelineColumn } from "./PipelineColumn";
import { PipelineCard } from "./PipelineCard";
import { getUserFriendlyError } from "../../lib/error-messages";
import { toast } from "sonner";

// ---------------------------------------------------------------------------
// PipelineKanban — full interactive kanban with drag-and-drop
// ---------------------------------------------------------------------------

interface PipelineKanbanProps {
  items: PipelineItem[];
  /** Original server items, used to revert optimistic updates on error. */
  sourceItems: PipelineItem[];
  onUpdateItem: (id: string, updates: { stage?: PipelineStage; notes?: string; version?: number }) => Promise<unknown>;
  onRemoveItem: (id: string) => Promise<unknown>;
  onFetchItems: (stage?: string) => Promise<unknown>;
}

export function PipelineKanban({
  items,
  sourceItems,
  onUpdateItem,
  onRemoveItem,
  onFetchItems,
}: PipelineKanbanProps) {
  const [activeItem, setActiveItem] = useState<PipelineItem | null>(null);
  const [optimisticItems, setOptimisticItems] = useState<PipelineItem[]>(items);

  // Keep optimistic state in sync whenever server items change
  useEffect(() => {
    setOptimisticItems(items);
  }, [items]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const getItemsByStage = useCallback(
    (stage: PipelineStage) => optimisticItems.filter((item) => item.stage === stage),
    [optimisticItems]
  );

  const handleDragStart = (event: DragStartEvent) => {
    const item = optimisticItems.find((i) => i.id === event.active.id);
    if (item) setActiveItem(item);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeItemData = optimisticItems.find((i) => i.id === activeId);
    if (!activeItemData) return;

    // Determine target stage: drop on column id or on another card
    const targetStage = STAGES_ORDER.includes(overId as PipelineStage)
      ? (overId as PipelineStage)
      : optimisticItems.find((i) => i.id === overId)?.stage;

    if (targetStage && targetStage !== activeItemData.stage) {
      setOptimisticItems((prev) =>
        prev.map((i) => (i.id === activeId ? { ...i, stage: targetStage } : i))
      );
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveItem(null);

    if (!over) return;

    const activeId = active.id as string;
    const item = optimisticItems.find((i) => i.id === activeId);
    const originalItem = sourceItems.find((i) => i.id === activeId);

    if (!item || !originalItem) return;

    if (item.stage !== originalItem.stage) {
      try {
        await onUpdateItem(activeId, { stage: item.stage, version: originalItem.version });
      } catch (err: unknown) {
        // Revert optimistic update
        setOptimisticItems(sourceItems);
        // STORY-307 AC11: On 409 conflict, show specific toast and reload
        const isConflict =
          err !== null &&
          typeof err === "object" &&
          "isConflict" in err &&
          (err as { isConflict: boolean }).isConflict;
        if (isConflict) {
          toast.error("Item foi atualizado por outra operação. Recarregando...");
          onFetchItems();
        } else {
          toast.error(getUserFriendlyError(err));
        }
      }
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div
        className="flex gap-4 overflow-x-auto pb-4 min-h-[calc(100vh-200px)]"
        data-tour="kanban-columns"
      >
        {STAGES_ORDER.map((stage) => (
          <PipelineColumn
            key={stage}
            stage={stage}
            items={getItemsByStage(stage)}
            onRemove={onRemoveItem}
            onUpdateNotes={(id, notes) => onUpdateItem(id, { notes })}
          />
        ))}
      </div>

      <DragOverlay>
        {activeItem ? <PipelineCard item={activeItem} isDragging /> : null}
      </DragOverlay>
    </DndContext>
  );
}

// ---------------------------------------------------------------------------
// ReadOnlyKanban — no sensors; used for trial-expired and error read-only modes
// ---------------------------------------------------------------------------

interface ReadOnlyKanbanProps {
  items: PipelineItem[];
}

export function ReadOnlyKanban({ items }: ReadOnlyKanbanProps) {
  const getItemsByStage = useCallback(
    (stage: PipelineStage) => items.filter((item) => item.stage === stage),
    [items]
  );

  return (
    <DndContext>
      <div className="flex gap-4 overflow-x-auto pb-4 min-h-[calc(100vh-200px)]">
        {STAGES_ORDER.map((stage) => (
          <PipelineColumn
            key={stage}
            stage={stage}
            items={getItemsByStage(stage)}
            onRemove={() => {}}
            onUpdateNotes={() => {}}
          />
        ))}
      </div>
    </DndContext>
  );
}
