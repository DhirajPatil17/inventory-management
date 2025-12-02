# AI Copilot Instructions for Inventory Management

## Project Overview

**Inventory Management System** - A Django-based web application for managing stock, suppliers, and bills (purchases/sales). Three main Django apps interact via shared database models: `inventory` (stock catalog), `transactions` (bills and suppliers), and `homepage` (dashboards).

**Tech Stack:** Django 3.1.13, SQLite, Bootstrap 4, django-crispy-forms, django-filter, django-login-required-middleware

## Architecture

### App Structure & Responsibilities

- **`inventory/`** - Stock management (CRUD operations)
  - Model: `Stock` (name, quantity, is_deleted flag)
  - Uses: FilterView with django-filter for search, class-based views (CBV)
  
- **`transactions/`** - Complex bill workflow (purchases/sales)
  - Models: `PurchaseBill`, `SaleBill` (parent), `PurchaseItem`, `SaleItem` (line items), `Supplier`, bill detail models
  - Uses: Formsets for multi-item entry, custom bill calculation logic in model methods
  
- **`homepage/`** - Dashboard & authentication landing
  - Views: HomeView (aggregates recent bills + stock chart data), AboutView
  - Login/logout handled by Django auth views in `core/urls.py`

### Data Flow Patterns

1. **Soft Deletion**: All entities use `is_deleted` boolean flag instead of hard deletion. Always filter with `is_deleted=False` in queries.
2. **Bill Calculations**: `PurchaseBill.get_total_price()` and `SaleBill.get_total_price()` iterate items; use these methods rather than raw aggregation.
3. **Cross-App References**: `transactions` imports from `inventory` (PurchaseItem/SaleItem ForeignKey to Stock).

## Key Development Patterns

### Views & Forms

**Standard CRUD with Mixins:**
```python
# inventory/views.py - Use this pattern
class StockCreateView(SuccessMessageMixin, CreateView):
    model = Stock
    form_class = StockForm
    success_url = '/inventory'
    success_message = "Stock has been created successfully"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Stock'
        context["savebtn"] = 'Add to Inventory'
        return context
```

**Context Customization**: All create/update views inject `title`, `savebtn`, and optionally `delbtn` for template reuse.

**Form Widget Styling**: Attach Bootstrap CSS classes in `__init__`:
```python
self.fields['name'].widget.attrs.update({'class': 'textinput form-control'})
```

**Formsets for Multi-Item Entry**: See `transactions/forms.py` - `PurchaseItemFormset` wraps `PurchaseItemForm` for dynamic bill line items.

### Filtering

Use `django_filters.FilterSet` for list views:
```python
class StockFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Stock
        fields = ['name']
```

Apply via `FilterView` in `inventory/views.py:StockListView`.

### Authentication & Authorization

- **Middleware**: `LoginRequiredMiddleware` enforces login globally (except whitelisted views in `settings.LOGIN_REQUIRED_IGNORE_VIEW_NAMES`)
- **Whitelisted URLs**: `login`, `logout`, `about`
- **Redirect**: Authenticated users see sidebar in `base.html` (template conditional: `{% if user.is_authenticated %}`)

## Database & Migrations

**First-time Setup** (see README):
```bash
python manage.py makemigrations homepage
python manage.py migrate homepage
python manage.py makemigrations inventory
python manage.py migrate inventory
python manage.py makemigrations transactions
python manage.py migrate transactions
```

**After Changes**: 
```bash
python manage.py makemigrations
python manage.py migrate
```

**Run Server**: `python manage.py runserver`

**Admin User**: `python manage.py createsuperuser`

## Common Workflows & Commands

| Task | Command |
|------|---------|
| Start development | `python manage.py runserver` |
| Apply model changes | `python manage.py makemigrations && python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Access admin | http://localhost:8000/admin |
| Django shell | `python manage.py shell` |

## Project-Specific Conventions

1. **Always check `is_deleted` flag** in queries (`Stock.objects.filter(is_deleted=False)`)
2. **Use model methods for calculations** (e.g., `bill.get_total_price()`) instead of aggregation queries
3. **Pass context variables** to forms in templates for reuse (title, savebtn, delbtn pattern)
4. **Template inheritance**: All pages extend `base.html` which manages sidebar + Bootstrap
5. **Pagination**: Use Django's `Paginator` class for large bill lists (see `transactions/views.py:SupplierView`)
6. **ForeignKey relationships**: Always define `related_name` (e.g., `related_name='purchasebillno'`) for reverse access

## File Organization

- **Models**: Each app has `models.py` with full domain logic (calculation methods, __str__)
- **Forms**: `forms.py` includes widget styling; formsets in same file
- **Views**: `views.py` uses class-based views (CBV) with SuccessMessageMixin
- **Templates**: Separate folders per app under `templates/` (e.g., `templates/suppliers/`, `templates/bill/`)
- **Static Files**: Bootstrap + custom CSS in `static/`, JS in `static/js/`

## Configuration Essentials

**`core/settings.py` Key Points:**
- INSTALLED_APPS: `homepage`, `inventory`, `transactions` (order matters for migration)
- TEMPLATES['DIRS']: `["templates"]` (root-level template directory)
- MIDDLEWARE: Custom `LoginRequiredMiddleware` for global auth enforcement
- LOGIN_REQUIRED_IGNORE_VIEW_NAMES: Whitelist views to allow unauthenticated access
- CRISPY_TEMPLATE_PACK: `'bootstrap4'` for form styling

## Integration Points & Dependencies

- **Stock Updates**: When a bill is created, manually update `Stock.quantity` (no automatic tracking)
- **Bill Relationships**: Supplier (1:N) PurchaseBill (1:N) PurchaseItem (N:1) Stock
- **GST Fields**: Stored as CharField in bill details (not integer) for flexibility
