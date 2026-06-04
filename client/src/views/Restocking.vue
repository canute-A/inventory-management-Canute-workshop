<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budgetLabel') }}</h3>
          <span class="budget-value">{{ currencySymbol }}{{ budget.toLocaleString() }}</span>
        </div>
        <input
          type="range"
          class="budget-slider"
          v-model.number="budget"
          min="0"
          max="50000"
          step="500"
          :aria-label="t('restocking.budgetLabel')"
        />
        <div class="slider-scale">
          <span>{{ currencySymbol }}0</span>
          <span>{{ currencySymbol }}25,000</span>
          <span>{{ currencySymbol }}50,000</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedTitle') }} ({{ recommendations.length }})</h3>
          <span class="hint">{{ t('restocking.howItWorks') }}</span>
        </div>

        <div v-if="!shortfallExists" class="empty-state">{{ t('restocking.allCovered') }}</div>
        <div v-else-if="recommendations.length === 0" class="empty-state">{{ t('restocking.budgetTooSmall') }}</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('orders.table.items') }}</th>
                <th>{{ t('restocking.gap') }}</th>
                <th>{{ t('restocking.orderQty') }}</th>
                <th>{{ t('restocking.coverage') }}</th>
                <th>{{ t('restocking.unitCost') }}</th>
                <th>{{ t('restocking.cost') }}</th>
                <th>{{ t('restocking.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in recommendations" :key="rec.item_sku">
                <td>
                  <strong>{{ translateProductName(rec.item_name) }}</strong>
                  <div class="sku">{{ rec.item_sku }}</div>
                </td>
                <td>{{ rec.gap.toLocaleString() }}</td>
                <td><strong>{{ rec.order_quantity.toLocaleString() }}</strong></td>
                <td>
                  <span :class="['badge', rec.partial ? 'warning' : 'success']">
                    {{ rec.partial ? t('restocking.partial') : t('restocking.full') }}
                  </span>
                </td>
                <td>{{ currencySymbol }}{{ rec.unit_cost.toFixed(2) }}</td>
                <td><strong>{{ currencySymbol }}{{ rec.cost.toLocaleString() }}</strong></td>
                <td>{{ rec.lead_time_days }} {{ t('restocking.days') }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="recommendations.length > 0" class="order-footer">
          <div class="totals">
            <div class="total-line">
              <span>{{ t('restocking.totalCost') }}</span>
              <strong>{{ currencySymbol }}{{ totalCost.toLocaleString() }}</strong>
            </div>
            <div class="total-line muted">
              <span>{{ t('restocking.remainingBudget') }}</span>
              <span>{{ currencySymbol }}{{ remainingBudget.toLocaleString() }}</span>
            </div>
          </div>
          <button class="place-order-btn" :disabled="submitting" @click="placeOrder">
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="confirmation" class="confirmation">
          {{ t('restocking.orderPlaced', { number: confirmation.order_number, days: confirmation.lead_time_days }) }}
          <router-link to="/orders">{{ t('restocking.viewInOrders') }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

// Demand-trend multipliers: a growing item with the same shortfall is more
// urgent than a shrinking one, because the gap widens during the lead time.
const TREND_WEIGHT = { increasing: 1.5, stable: 1.0, decreasing: 0.5 }

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()
    const currencySymbol = computed(() => currentCurrency.value === 'JPY' ? '¥' : '$')

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(10000)
    const submitting = ref(false)
    const confirmation = ref(null)

    const shortfalls = computed(() =>
      forecasts.value
        .map(f => ({ ...f, gap: Math.max(0, f.forecasted_demand - f.quantity_on_hand) }))
        .filter(f => f.gap > 0)
    )

    const shortfallExists = computed(() => shortfalls.value.length > 0)

    // Urgency-first greedy: rank by (gap as a share of forecasted demand,
    // weighted by trend), then spend the budget top-down. The last affordable
    // item may be partially covered so small budget increases stay visible.
    const recommendations = computed(() => {
      const ranked = shortfalls.value
        .map(f => ({
          ...f,
          urgency: (f.gap / Math.max(f.forecasted_demand, 1)) * (TREND_WEIGHT[f.trend] || 1)
        }))
        .sort((a, b) => b.urgency - a.urgency)

      let remaining = budget.value
      const picks = []
      for (const item of ranked) {
        const affordable = Math.floor(remaining / item.unit_cost)
        const quantity = Math.min(item.gap, affordable)
        if (quantity <= 0) continue
        const cost = Math.round(quantity * item.unit_cost * 100) / 100
        picks.push({ ...item, order_quantity: quantity, cost, partial: quantity < item.gap })
        remaining -= cost
      }
      return picks
    })

    const totalCost = computed(() =>
      Math.round(recommendations.value.reduce((sum, r) => sum + r.cost, 0) * 100) / 100
    )

    const remainingBudget = computed(() =>
      Math.round((budget.value - totalCost.value) * 100) / 100
    )

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      try {
        submitting.value = true
        confirmation.value = null
        confirmation.value = await api.createRestockOrder({
          budget: budget.value,
          items: recommendations.value.map(r => ({
            sku: r.item_sku,
            name: r.item_name,
            quantity: r.order_quantity,
            unit_cost: r.unit_cost,
            lead_time_days: r.lead_time_days
          }))
        })
      } catch (err) {
        error.value = 'Failed to place order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      translateProductName,
      currencySymbol,
      loading,
      error,
      budget,
      shortfallExists,
      recommendations,
      totalCost,
      remainingBudget,
      submitting,
      confirmation,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
}

.budget-slider {
  width: 100%;
  accent-color: #2563eb;
  cursor: pointer;
  margin: 0.5rem 0 0.25rem;
}

.slider-scale {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
}

.hint {
  font-size: 0.813rem;
  color: #64748b;
  max-width: 55%;
  text-align: right;
}

.sku {
  font-size: 0.75rem;
  color: #64748b;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.order-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.totals {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 260px;
}

.total-line {
  display: flex;
  justify-content: space-between;
  font-size: 0.938rem;
  color: #0f172a;
}

.total-line.muted {
  color: #64748b;
  font-size: 0.875rem;
}

.place-order-btn {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.confirmation {
  margin-top: 1rem;
  padding: 0.875rem 1rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 8px;
  font-size: 0.938rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.confirmation a {
  color: #065f46;
  font-weight: 600;
}
</style>
