from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders

app = FastAPI(title="Factory Inventory Management System")

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str
    quantity_on_hand: int
    unit_cost: float
    lead_time_days: int

class PurchaseOrderInfo(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False
    purchase_order_id: Optional[str] = None
    purchase_order: Optional[PurchaseOrderInfo] = None

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    notes: Optional[str] = None

class RestockOrderItem(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_cost: float
    lead_time_days: int

class RestockOrder(BaseModel):
    id: str
    order_number: str
    status: str
    submitted_at: str
    budget: float
    total_cost: float
    items: List[RestockOrderItem]
    lead_time_days: int
    expected_delivery: str

class CreateRestockOrderRequest(BaseModel):
    budget: float
    items: List[RestockOrderItem]

# camelCase dueDate matches the frontend task shape (TasksModal/useAuth), unlike
# the snake_case used elsewhere in this API
class Task(BaseModel):
    id: int
    title: str
    priority: str
    dueDate: str
    status: str

class CreateTaskRequest(BaseModel):
    title: str
    priority: str
    dueDate: str

# Submitted restocking orders, in-memory like all other data (reset on restart)
restock_orders: list = []

# User tasks, in-memory like all other data (reset on restart).
# IDs start at 1000: the frontend seeds mock tasks with low numeric ids and uses
# the id to decide whether a task is mock (local) or API-backed, so they must not collide.
tasks: list = []
next_task_id = 1000

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/restock-orders", response_model=List[RestockOrder])
def get_restock_orders():
    """Get all submitted restocking orders"""
    return restock_orders

@app.post("/api/restock-orders", response_model=RestockOrder)
def create_restock_order(request: CreateRestockOrderRequest):
    """Submit a restocking order built from demand-forecast recommendations"""
    if not request.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")
    total_cost = round(sum(i.quantity * i.unit_cost for i in request.items), 2)
    if total_cost > request.budget:
        raise HTTPException(status_code=400, detail="Order total exceeds the stated budget")
    now = datetime.now()
    # Delivery is gated by the slowest supplier in the order
    lead_time = max(i.lead_time_days for i in request.items)
    order = {
        "id": str(len(restock_orders) + 1),
        "order_number": f"RST-{now.year}-{len(restock_orders) + 1:04d}",
        "status": "Submitted",
        "submitted_at": now.isoformat(timespec="seconds"),
        "budget": request.budget,
        "total_cost": total_cost,
        "items": [i.dict() for i in request.items],
        "lead_time_days": lead_time,
        "expected_delivery": (now + timedelta(days=lead_time)).isoformat(timespec="seconds"),
    }
    restock_orders.append(order)
    return order

@app.get("/api/tasks", response_model=List[Task])
def get_tasks():
    """Get all user tasks"""
    return tasks

@app.post("/api/tasks", response_model=Task)
def create_task(request: CreateTaskRequest):
    """Create a new task"""
    global next_task_id
    task = {
        "id": next_task_id,
        "title": request.title,
        "priority": request.priority,
        "dueDate": request.dueDate,
        "status": "pending",
    }
    next_task_id += 1
    tasks.append(task)
    return task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task"""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks.remove(task)
    return {"status": "deleted", "id": task_id}

@app.patch("/api/tasks/{task_id}", response_model=Task)
def toggle_task(task_id: int):
    """Toggle a task between pending and completed"""
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = "completed" if task["status"] == "pending" else "pending"
    return task

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Attach the purchase order (if any) so the UI can show View PO after a reload
        po = next((po for po in purchase_orders if po["backlog_item_id"] == item["id"]), None)
        item_dict["has_purchase_order"] = po is not None
        item_dict["purchase_order_id"] = po["id"] if po else None
        item_dict["purchase_order"] = po
        result.append(item_dict)
    return result

@app.post("/api/purchase-orders", response_model=PurchaseOrderInfo)
def create_purchase_order(request: CreatePurchaseOrderRequest):
    """Create a purchase order for a backlog item"""
    backlog_item = next((b for b in backlog_items if b["id"] == request.backlog_item_id), None)
    if not backlog_item:
        raise HTTPException(status_code=404, detail="Backlog item not found")
    if any(po["backlog_item_id"] == request.backlog_item_id for po in purchase_orders):
        raise HTTPException(status_code=400, detail="A purchase order already exists for this backlog item")
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    now = datetime.now()
    po = {
        "id": f"PO-{now.year}-{len(purchase_orders) + 1:04d}",
        "backlog_item_id": request.backlog_item_id,
        "supplier_name": request.supplier_name,
        "quantity": request.quantity,
        "unit_cost": request.unit_cost,
        "expected_delivery_date": request.expected_delivery_date,
        "status": "Ordered",
        "created_date": now.isoformat(timespec="seconds"),
        "notes": request.notes,
    }
    purchase_orders.append(po)
    return po

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders)
    }

MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def spending_month_names(month: Optional[str]) -> Optional[list]:
    """Map a global Time Period value (YYYY-MM or Q#-2025) to monthly_spending month labels"""
    if not month or month == 'all':
        return None
    if month.startswith('Q') and month in QUARTER_MAP:
        return [MONTH_NAMES[int(m[5:7]) - 1] for m in QUARTER_MAP[month]]
    try:
        return [MONTH_NAMES[int(month[5:7]) - 1]]
    except (ValueError, IndexError):
        return None

@app.get("/api/spending/summary")
def get_spending_summary(month: Optional[str] = None):
    """Spending summary; a month/quarter narrows totals (derived from monthly_spending).
    Warehouse/category/status filters don't apply: spend data has no such dimensions."""
    names = spending_month_names(month)
    if not names:
        return spending_summary
    rows = [m for m in monthly_spending if m['month'] in names]
    keymap = {
        'procurement': ('total_procurement_cost', 'procurement_change'),
        'operational': ('total_operational_cost', 'operational_change'),
        'labor': ('total_labor_cost', 'labor_change'),
        'overhead': ('total_overhead', 'overhead_change'),
    }
    result = {}
    # Change% is month-over-month, so it is only meaningful for a single-month selection
    prev = None
    if len(rows) == 1:
        idx = MONTH_NAMES.index(rows[0]['month'])
        prev = monthly_spending[idx - 1] if idx > 0 else None
    for src, (total_key, change_key) in keymap.items():
        total = sum(r[src] for r in rows)
        result[total_key] = total
        result[change_key] = round((total - prev[src]) / prev[src] * 100, 1) if prev and prev[src] else 0
    return result

@app.get("/api/spending/monthly")
def get_monthly_spending(month: Optional[str] = None):
    """Get monthly spending breakdown, optionally narrowed to a month/quarter"""
    names = spending_month_names(month)
    if not names:
        return monthly_spending
    return [m for m in monthly_spending if m['month'] in names]

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category (all-time: category data has no month dimension)"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions(month: Optional[str] = None):
    """Get recent transactions, optionally filtered to a month/quarter by date"""
    if not month or month == 'all':
        return recent_transactions
    if month.startswith('Q') and month in QUARTER_MAP:
        months = QUARTER_MAP[month]
        return [t for t in recent_transactions if t.get('date', '')[:7] in months]
    return [t for t in recent_transactions if t.get('date', '').startswith(month)]

@app.get("/api/reports/quarterly")
def get_quarterly_reports(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get quarterly performance reports, honoring the same global filters as /api/orders"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    # Calculate quarterly statistics from orders
    quarters = {}

    for order in filtered_orders:
        order_date = order.get('order_date', '')
        # Determine quarter
        if '2025-01' in order_date or '2025-02' in order_date or '2025-03' in order_date:
            quarter = 'Q1-2025'
        elif '2025-04' in order_date or '2025-05' in order_date or '2025-06' in order_date:
            quarter = 'Q2-2025'
        elif '2025-07' in order_date or '2025-08' in order_date or '2025-09' in order_date:
            quarter = 'Q3-2025'
        elif '2025-10' in order_date or '2025-11' in order_date or '2025-12' in order_date:
            quarter = 'Q4-2025'
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    # Calculate averages and fulfillment rate
    result = []
    for q, data in quarters.items():
        if data['total_orders'] > 0:
            data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
            data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    # Sort by quarter
    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get month-over-month trends, honoring the same global filters as /api/orders"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    months = {}

    for order in filtered_orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        month = order_date[:7]  # Gets YYYY-MM

        if month not in months:
            months[month] = {
                'month': month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[month]['order_count'] += 1
        months[month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
