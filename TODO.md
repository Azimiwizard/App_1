# Dish Management Enhancements TODO

## 1. Input Validation
- [x] Add WTForms dependency to requirements.txt
- [x] Create forms.py with DishForm
- [x] Update admin_add_dish route to use form validation
- [x] Update admin_edit_dish route to use form validation
- [x] Update templates to display validation errors

## 2. Image Upload Feature
- [x] Create static/uploads directory
- [x] Update Dish model to store image filename instead of URL
- [x] Modify admin_add_dish route to handle file upload
- [x] Modify admin_edit_dish route to handle file upload
- [x] Update templates to use file input instead of URL
- [x] Add image display logic in templates

## 3. Dynamic Sections
- [ ] Create Section model
- [ ] Add admin routes for section CRUD
- [ ] Update Dish model to reference Section
- [ ] Update forms to use dynamic sections
- [ ] Create admin_sections.html template
- [ ] Update menu logic to use dynamic sections

## 4. Dish Cloning
- [ ] Add clone route in main.py
- [ ] Add clone button in admin_dashboard.html
- [ ] Handle image copying for cloned dishes

## 5. Search and Filter in Admin
- [ ] Update admin_dashboard route to accept query params
- [ ] Add search form in admin_dashboard.html
- [ ] Implement filtering logic

## 6. Bulk Add Functionality
- [ ] Add bulk_add route
- [ ] Create bulk_add.html template
- [ ] Implement CSV parsing logic
- [ ] Add bulk add button in admin dashboard

## 7. Rich Text Descriptions
- [ ] Add TinyMCE dependency
- [ ] Update templates to include TinyMCE
- [ ] Update forms to handle HTML content

## 8. Preview Before Save
- [ ] Add preview modal in add/edit templates
- [ ] Create preview logic (simulate menu display)

## 9. Audit Logging
- [ ] Create AuditLog model
- [ ] Add logging to dish CRUD operations
- [ ] Create admin_audit_logs.html template

## 10. API Endpoints
- [ ] Add API routes for dish CRUD
- [ ] Implement JSON responses
- [ ] Add authentication for API
