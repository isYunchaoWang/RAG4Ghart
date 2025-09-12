import { Typography, Button, Space, Popconfirm } from 'antd'
import { DeleteOutlined, HolderOutlined } from '@ant-design/icons'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import {
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

const { Text } = Typography

function SortableItem({ item, index, onSelect, onDelete }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.id || index })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={{
        ...style,
        border: '1px solid #f0f0f0',
        borderRadius: 6,
        padding: 8,
        minWidth: 160,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        position: 'relative',
        background: isDragging ? '#f0f8ff' : 'white',
        cursor: isDragging ? 'grabbing' : 'grab'
      }}
    >
      {/* Drag handle */}
      <div
        {...attributes}
        {...listeners}
        style={{
          position: 'absolute',
          top: 4,
          left: 4,
          zIndex: 1,
          color: '#999',
          cursor: 'grab',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 20,
          height: 20,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.9)',
          border: '1px solid #e0e0e0'
        }}
      >
        <HolderOutlined style={{ fontSize: 12 }} />
      </div>

      {/* Delete button */}
      <Popconfirm
        title="Are you sure you want to delete this record?"
        onConfirm={(e) => {
          e.stopPropagation()
          onDelete(index)
        }}
        onCancel={(e) => e.stopPropagation()}
        okText="Confirm"
        cancelText="Cancel"
      >
        <Button
          type="text"
          size="small"
          icon={<DeleteOutlined />}
          style={{
            position: 'absolute',
            top: 4,
            right: 4,
            zIndex: 1,
            color: '#ff4d4f',
            background: 'rgba(255, 255, 255, 0.9)',
            border: 'none',
            borderRadius: '50%',
            width: 24,
            height: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onClick={(e) => e.stopPropagation()}
        />
      </Popconfirm>
      
      {/* Chart content */}
      <div 
        style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', marginTop: 8 }}
        onClick={() => onSelect(item, index)}
      >
        {item.thumb ? (
          <img src={item.thumb} alt={item.title || `Record ${index + 1}`} style={{ width: 140, height: 100, objectFit: 'contain', background: '#fafafa', borderRadius: 4, marginBottom: 6 }} />
        ) : (
          <div style={{ width: 140, height: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa', borderRadius: 4, marginBottom: 6 }}>
            <Text type="secondary">No Preview</Text>
          </div>
        )}
        <div style={{ fontWeight: 500, maxWidth: 140, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title || `记录 ${index + 1}`}</div>
      </div>
    </div>
  )
}

function ChartHistory({ items, onSelect, onClear, onDelete, onReorder }) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = (event) => {
    const { active, over } = event

    if (active.id !== over.id) {
      const oldIndex = items.findIndex(item => (item.id || items.indexOf(item)) === active.id)
      const newIndex = items.findIndex(item => (item.id || items.indexOf(item)) === over.id)
      
      onReorder(oldIndex, newIndex)
    }
  }

  // 为每个item添加唯一ID（如果没有的话）
  const itemsWithIds = items.map((item, index) => ({
    ...item,
    id: item.id || index
  }))
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      {/* Clear button - top right corner */}
      <Button 
        size="small" 
        onClick={onClear}
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          zIndex: 2
        }}
      >
        Clear
      </Button>
      <div style={{ flex: 1, overflowX: 'auto', overflowY: 'hidden' }}>
        {Array.isArray(items) && items.length > 0 ? (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={itemsWithIds.map(item => item.id)}
              strategy={verticalListSortingStrategy}
            >
              <div style={{ display: 'flex', gap: 8 }}>
                {itemsWithIds.map((item, index) => (
                  <SortableItem
                    key={item.id}
                    item={item}
                    index={index}
                    onSelect={onSelect}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        ) : (
          <div style={{ color: '#999' }}>No history</div>
        )}
      </div>
    </div>
  )
}

export default ChartHistory 