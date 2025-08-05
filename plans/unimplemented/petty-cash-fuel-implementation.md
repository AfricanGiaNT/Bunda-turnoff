# Petty Cash & Fuel Logs Implementation Plan

**Goal:** Implement core functionality for logging petty cash expenses and fuel logs via Telegram → GPT → Airtable.

**Based on:** Actual Airtable base analysis completed on 2025-08-04

## 📊 **Airtable Schema Analysis**

### **Petty Cash Table** (`tblzh9vb96VrEvwZU`)
**Required Fields for MVP:**
- `Person` (singleLineText) - Who incurred the expense
- `Amount` (currency) - Amount spent  
- `Description` (multilineText) - What it was for
- `Date` (date) - Transaction date
- `Receipt Photo` (multipleAttachments) - Optional photo of receipt

**Calculated Fields (Auto-generated):**
- `Theoretical Balance` (number) - Calculated balance
- `Actual Balance` (currency) - Manual input of actual float
- `Reconciliation Diff` (number) - Difference between theoretical and actual

### **Fuel Logs Table** (`tblokwpw2cvNp5I8M`)
**Required Fields for MVP:**
- `Driver` (singleLineText) - Driver name
- `Vehicle` (singleSelect) - Vehicle selection (Toyota Hilux, Toyota Prado, Other)
- `Date` (date) - Fueling date
- `Liters` (number) - Quantity dispensed
- `Odometer Start` (number) - Before trip
- `Odometer End` (number) - After trip
- `Purpose` (multilineText) - Reason/destination
- `Logged By` (singleLineText) - Who logged the entry

**Calculated Fields (Auto-generated):**
- `KMs Travelled` (number) - Calculated distance
- `Fuel Efficiency` (formula) - Calculated efficiency

## 🎯 **Implementation Steps**

### **Phase 1: Core Infrastructure (Day 1)**
- [x] **1.1** Update Airtable client with actual table IDs and field mappings
- [x] **1.2** Implement GPT parser for petty cash and fuel log messages
- [x] **1.3** Create Telegram message handler for natural language processing
- [x] **1.4** Add retry logic and error handling for Airtable operations
- [x] **1.5** Test end-to-end flow with sample messages

### **Phase 2: Petty Cash Implementation (Day 1)**
- [x] **2.1** Implement petty cash expense creation
- [ ] **2.2** Add theoretical balance calculation logic
- [x] **2.3** Handle receipt photo attachments
- [x] **2.4** Create confirmation messages with balance updates
- [x] **2.5** Test petty cash logging with various scenarios

### **Phase 3: Fuel Logs Implementation (Day 2)**
- [x] **3.1** Implement fuel log creation with vehicle selection
- [x] **3.2** Add odometer calculation (KMs Travelled)
- [x] **3.3** Handle fuel efficiency calculations
- [x] **3.4** Create confirmation messages with efficiency metrics
- [x] **3.5** Test fuel logging with different vehicles and scenarios

### **Phase 4: Integration & Testing (Day 2)**
- [ ] **4.1** Test both petty cash and fuel logs together
- [ ] **4.2** Add error handling for edge cases
- [ ] **4.3** Implement fallback clarifier for ambiguous messages
- [ ] **4.4** Create help command with usage examples
- [ ] **4.5** Test with real Telegram bot

## 🤖 **GPT Prompt Design**

### **Petty Cash Examples:**
```
User: "Paid 15,000 MWK for filter replacement from petty cash"
GPT Output: {
  "type": "expense",
  "date": "2025-08-04",
  "amount": 15000,
  "description": "Filter replacement",
  "person": "Me"
}

User: "Spent 25,000 on generator fuel, receipt attached"
GPT Output: {
  "type": "expense", 
  "date": "2025-08-04",
  "amount": 25000,
  "description": "Generator fuel",
  "person": "Me",
  "receipt_url": "attached"
}
```

### **Fuel Log Examples:**
```
User: "Gave 40 liters diesel to Hilux, driver John, for Salima trip. Odometer start 12300 end 12420"
GPT Output: {
  "type": "fuel",
  "date": "2025-08-04", 
  "vehicle": "Toyota Hilux",
  "driver": "John",
  "liters": 40,
  "odometer_start": 12300,
  "odometer_end": 12420,
  "purpose": "Salima trip"
}

User: "Prado refueled 35L, driver Sarah, odometer 15600 to 15800, maintenance visit"
GPT Output: {
  "type": "fuel",
  "date": "2025-08-04",
  "vehicle": "Toyota Prado", 
  "driver": "Sarah",
  "liters": 35,
  "odometer_start": 15600,
  "odometer_end": 15800,
  "purpose": "Maintenance visit"
}
```

## 🔧 **Technical Implementation**

### **Airtable Field Mappings:**
```python
PETTY_CASH_FIELDS = {
    'person': 'Person',
    'amount': 'Amount', 
    'description': 'Description',
    'date': 'Date',
    'receipt_photo': 'Receipt Photo'
}

FUEL_LOG_FIELDS = {
    'driver': 'Driver',
    'vehicle': 'Vehicle',
    'date': 'Date', 
    'liters': 'Liters',
    'odometer_start': 'Odometer Start',
    'odometer_end': 'Odometer End',
    'purpose': 'Purpose',
    'logged_by': 'Logged By'
}
```

### **Error Handling:**
- Missing required fields → Ask for clarification
- Invalid vehicle selection → Suggest valid options
- Odometer calculation errors → Validate start < end
- Airtable API errors → Retry with exponential backoff

## ✅ **Success Criteria**
- [ ] Can log petty cash expenses via natural language
- [ ] Can log fuel entries with vehicle selection and odometer
- [ ] Theoretical balance updates correctly for petty cash
- [ ] KMs travelled and fuel efficiency calculated automatically
- [ ] Confirmation messages show relevant information
- [ ] Error handling works for edge cases
- [ ] Help command provides clear usage examples

## 🚀 **Next Steps**
1. Update `airtable_client.py` with actual table IDs and field mappings
2. Implement GPT parser for the two message types
3. Create Telegram handler for processing messages
4. Test with sample data
5. Deploy and test with real bot

---

**Created:** 2025-08-04
**Status:** Unimplemented
**Priority:** High (Core MVP functionality) 