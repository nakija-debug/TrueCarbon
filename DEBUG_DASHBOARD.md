# Dashboard Debug Guide

## Issue: Dashboard showing mock data instead of user-created data

### Step-by-Step Testing Instructions

#### 1. **Clear Browser Data**
   - Open browser DevTools (F12 or Cmd+Option+I)
   - Go to "Storage" → "LocalStorage"
   - Delete all entries for localhost:3001
   - Refresh the page

#### 2. **Open Console**
   - Keep DevTools open to "Console" tab
   - Set filter to "All levels" so you see all logs

#### 3. **Perform the Flow**
   - **Sign Up:**
     - Email: `test@example.com`
     - Name: `Test User`
     - Company: `Test Company`
     - Watch console for logs
   
   - **Company Details:**
     - Fill all fields
     - Click "Continue to Farm Setup"
     - Watch console
   
   - **Farm Form:**
     - Farm Name: `My Test Farm`
     - Draw polygon on map (multiple clicks, double-click to finish)
     - Click "✅ SAVE LAND AREA" button
     - Promised Credits: `50`
     - Click "✅ Create Farm & Fetch Satellite Data"
     
#### 4. **Check Console Output**

Look for these specific log messages (in order):
```
📋 Form Values at submission: {farmName: "My Test Farm", areaHa: "...", ...}
🚀 About to call onSuccess with: {name: "My Test Farm", ...}
✅ Calling onSuccess callback
✅ Farm created callback triggered with: {...}
💾 Saving to localStorage: {company: {...}, farms: [{...}], ...}
✅ Dashboard data saved to localStorage
📊 Farms now in storage: 1

🎯 Dashboard rendering
dashboardDataFromStorage: {"company":{...},"farms":[{...}], ...}
userDashboardData: {company: {...}, farms: [{...}], ...}
userDashboardData?.farms?.length: 1
🎯 Dashboard using farms: 1 Total Area: X Total Credits: Y
```

#### 5. **Check LocalStorage**
   - In DevTools → Storage → LocalStorage → localhost:3001
   - Look for `dashboardData` key
   - It should contain your farm data, NOT empty

#### 6. **Expected Dashboard Display**
   - Header should show: "Welcome, Test User | Test Company"
   - KPI cards should show YOUR values (not Amazon/Mangrove/Savanna mock data)
   - "Your Carbon Credit Projects" table should show: "My Test Farm"

### If Dashboard Shows Mock Data (Problem Persists)

#### Check #1: Is onSuccess being called?
- Look for "✅ Calling onSuccess callback" in console
- If missing: Form submission failing silently
- If present: Problem is downstream

#### Check #2: Is localStorage.setItem working?
- Look for "💾 Saving to localStorage:" in console
- Go to DevTools → Storage → LocalStorage
- Check if `dashboardData` key exists
- If missing: localStorage failed or Dashboard not rendering after setState

#### Check #3: Is Dashboard reading localStorage?
- Look for "dashboardDataFromStorage:" value in console
- Should contain yourfarm data, not null
- If null: localStorage.setItem didn't work OR Dashboard rendered before data was saved

### Common Issues & Solutions

**Issue: onSuccess not called**
- Check that all form fields are filled
- Check that polygon is drawn (SAVE LAND AREA must be clicked)
- Check browser console for errors in farm-form.tsx

**Issue: localStorage data is null in Dashboard**
- React state updates are async, but localStorage is sync
- Check that setShowFarmForm(false) and setIsLoggedIn(true) are called AFTER localStorage.setItem
- Current code structure is correct, but timing issues are possible

**Issue: Failed to draw polygon**
- Click on map to start drawing
- Click to add points
- Double-click to finish
- Make sure "SAVE LAND AREA" button appears and click it
- Area field should auto-fill with hectares calculation
