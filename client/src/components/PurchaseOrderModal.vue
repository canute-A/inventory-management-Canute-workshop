<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="close">
        <div class="modal-container po-modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'create' ? t('purchaseOrder.createTitle') : t('purchaseOrder.viewTitle') }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <!-- Backlog item context shown in both modes -->
            <div v-if="backlogItem" class="item-context">
              <div class="context-header">{{ t('purchaseOrder.itemContext') }}</div>
              <div class="context-grid">
                <div class="context-item">
                  <span class="context-label">{{ t('purchaseOrder.itemName') }}</span>
                  <span class="context-value">{{ backlogItem.item_name }}</span>
                </div>
                <div class="context-item">
                  <span class="context-label">{{ t('purchaseOrder.sku') }}</span>
                  <span class="context-value mono">{{ backlogItem.item_sku }}</span>
                </div>
                <div class="context-item">
                  <span class="context-label">{{ t('purchaseOrder.shortage') }}</span>
                  <span class="context-value shortage-badge">
                    {{ shortage }} {{ t('dashboard.inventoryShortages.unitsShort') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Create mode: form -->
            <div v-if="mode === 'create'" class="po-form">
              <div class="form-group">
                <label for="po-supplier-name">{{ t('purchaseOrder.supplierName') }} *</label>
                <input
                  id="po-supplier-name"
                  v-model="form.supplier_name"
                  type="text"
                  :placeholder="t('purchaseOrder.supplierNamePlaceholder')"
                  class="form-input"
                />
              </div>

              <div class="form-row-two">
                <div class="form-group">
                  <label for="po-quantity">{{ t('purchaseOrder.quantity') }} *</label>
                  <input
                    id="po-quantity"
                    v-model.number="form.quantity"
                    type="number"
                    min="1"
                    class="form-input"
                  />
                </div>
                <div class="form-group">
                  <label for="po-unit-cost">{{ t('purchaseOrder.unitCost') }} *</label>
                  <input
                    id="po-unit-cost"
                    v-model.number="form.unit_cost"
                    type="number"
                    step="0.01"
                    min="0"
                    class="form-input"
                  />
                </div>
              </div>

              <div class="form-group">
                <label for="po-delivery-date">{{ t('purchaseOrder.expectedDeliveryDate') }} *</label>
                <input
                  id="po-delivery-date"
                  v-model="form.expected_delivery_date"
                  type="date"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="po-notes">{{ t('purchaseOrder.notes') }}</label>
                <textarea
                  id="po-notes"
                  v-model="form.notes"
                  :placeholder="t('purchaseOrder.notesPlaceholder')"
                  class="form-textarea"
                  rows="3"
                ></textarea>
              </div>

              <div v-if="submitError" class="submit-error">{{ submitError }}</div>
            </div>

            <!-- View mode: read-only PO details -->
            <div
              v-else-if="mode === 'view' && backlogItem && backlogItem.purchase_order"
              class="po-details"
            >
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.orderId') }}</span>
                <span class="detail-value mono">{{ backlogItem.purchase_order.id }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.supplierName') }}</span>
                <span class="detail-value">{{ backlogItem.purchase_order.supplier_name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.quantity') }}</span>
                <span class="detail-value">{{ backlogItem.purchase_order.quantity }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.unitCost') }}</span>
                <span class="detail-value">${{ Number(backlogItem.purchase_order.unit_cost).toFixed(2) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.totalValue') }}</span>
                <span class="detail-value">
                  ${{ (backlogItem.purchase_order.quantity * backlogItem.purchase_order.unit_cost).toFixed(2) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.expectedDeliveryDate') }}</span>
                <span class="detail-value">{{ backlogItem.purchase_order.expected_delivery_date }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.status') }}</span>
                <span class="detail-value">
                  <span :class="['badge', getStatusBadge(backlogItem.purchase_order.status)]">
                    {{ backlogItem.purchase_order.status }}
                  </span>
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.createdDate') }}</span>
                <span class="detail-value">{{ backlogItem.purchase_order.created_date }}</span>
              </div>
              <div v-if="backlogItem.purchase_order.notes" class="detail-row">
                <span class="detail-label">{{ t('purchaseOrder.notes') }}</span>
                <span class="detail-value">{{ backlogItem.purchase_order.notes }}</span>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">{{ t('common.cancel') }}</button>
            <button
              v-if="mode === 'create'"
              class="btn-primary"
              :disabled="submitting || !isFormValid"
              @click="handleSubmit"
            >
              {{ submitting ? t('purchaseOrder.submitting') : t('purchaseOrder.submit') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'PurchaseOrderModal',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    backlogItem: {
      type: Object,
      default: null
    },
    mode: {
      type: String,
      default: 'create' // 'create' or 'view'
    }
  },
  emits: ['close', 'po-created'],
  setup(props, { emit }) {
    const { t } = useI18n()

    const submitting = ref(false)
    const submitError = ref(null)

    const form = ref({
      supplier_name: '',
      quantity: 1,
      unit_cost: 0,
      expected_delivery_date: '',
      notes: ''
    })

    // Units short for this backlog item
    const shortage = computed(() => {
      if (!props.backlogItem) return 0
      return Math.max(0, (props.backlogItem.quantity_needed || 0) - (props.backlogItem.quantity_available || 0))
    })

    // Reset and pre-fill form whenever the modal opens in create mode
    watch(
      () => props.isOpen,
      (newVal) => {
        if (newVal && props.mode === 'create') {
          form.value = {
            supplier_name: '',
            quantity: shortage.value || 1,
            unit_cost: 0,
            expected_delivery_date: '',
            notes: ''
          }
          submitError.value = null
        }
      }
    )

    const isFormValid = computed(() => {
      return (
        form.value.supplier_name.trim().length > 0 &&
        form.value.quantity >= 1 &&
        form.value.unit_cost >= 0 &&
        form.value.expected_delivery_date.length > 0
      )
    })

    const close = () => {
      emit('close')
    }

    const handleSubmit = async () => {
      if (!isFormValid.value) return

      submitting.value = true
      submitError.value = null

      try {
        const poData = await api.createPurchaseOrder({
          backlog_item_id: props.backlogItem.id,
          supplier_name: form.value.supplier_name.trim(),
          quantity: form.value.quantity,
          unit_cost: form.value.unit_cost,
          expected_delivery_date: form.value.expected_delivery_date,
          notes: form.value.notes || null
        })
        emit('po-created', poData)
      } catch (err) {
        if (err.response && err.response.data && err.response.data.detail) {
          submitError.value = err.response.data.detail
        } else {
          submitError.value = t('purchaseOrder.errorDuplicate')
        }
      } finally {
        submitting.value = false
      }
    }

    const getStatusBadge = (status) => {
      if (!status) return ''
      const s = status.toLowerCase()
      if (s === 'approved' || s === 'completed' || s === 'received') return 'success'
      if (s === 'pending' || s === 'submitted') return 'warning'
      if (s === 'cancelled' || s === 'rejected') return 'danger'
      return ''
    }

    return {
      t,
      form,
      shortage,
      submitting,
      submitError,
      isFormValid,
      close,
      handleSubmit,
      getStatusBadge
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  padding: 1.5rem 2rem;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-footer {
  padding: 1.25rem 2rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* Item context block */
.item-context {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem 1.25rem;
}

.context-header {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.75rem;
}

.context-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.context-label {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.context-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.context-value.mono {
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.813rem;
}

.shortage-badge {
  color: #dc2626;
}

/* Create form */
.po-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.form-input {
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  transition: border-color 0.15s ease;
  font-family: inherit;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  transition: border-color 0.15s ease;
  font-family: inherit;
  resize: vertical;
  min-height: 72px;
  background: white;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.submit-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #dc2626;
}

/* View mode details */
.po-details {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
  gap: 1rem;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 0.813rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.detail-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
  text-align: right;
}

.detail-value.mono {
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.813rem;
}

/* Buttons */
.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  padding: 0.625rem 1.5rem;
  background: #3b82f6;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Badge (mirrors global badge styles for PO status) */
.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.badge.danger {
  background: #fecaca;
  color: #991b1b;
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
