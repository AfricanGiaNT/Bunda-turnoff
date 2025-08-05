# Tasks & Issues Implementation Plan

## 📋 **Current Status**
- ✅ **Petty Cash & Fuel Logs**: Fully implemented and working
- ✅ **Telegram Bot**: Connected and processing messages
- ✅ **GPT Parser**: Natural language processing pipeline
- ✅ **Airtable Integration**: Database storage working
- 🔄 **Tasks & Issues**: Ready for implementation

## 🎯 **Implementation Goals**

### **Phase 1: Core Infrastructure (Day 1)**
- [ ] **1.1** Extend GPT parser to handle task and issue messages
- [ ] **1.2** Update Airtable client with task and issue field mappings
- [ ] **1.3** Add task and issue validation logic
- [ ] **1.4** Create confirmation message generators for tasks/issues
- [ ] **1.5** Test basic parsing and storage

### **Phase 2: Tasks Implementation (Day 1)**
- [ ] **2.1** Implement task message parsing
- [ ] **2.2** Add task field mappings to Airtable client
- [ ] **2.3** Create task validation logic
- [ ] **2.4** Test task creation with various message formats
- [ ] **2.5** Add task-specific confirmation messages

### **Phase 3: Issues Implementation (Day 1)**
- [ ] **3.1** Implement issue message parsing
- [ ] **3.2** Add issue field mappings to Airtable client
- [ ] **3.3** Create issue validation logic
- [ ] **3.4** Test issue creation with various message formats
- [ ] **3.5** Add issue-specific confirmation messages

### **Phase 4: Integration & Testing (Day 2)**
- [ ] **4.1** Test all four message types together (expense, fuel, task, issue)
- [ ] **4.2** Add error handling for edge cases
- [ ] **4.3** Implement fallback clarifier for ambiguous messages
- [ ] **4.4** Create help command with usage examples
- [ ] **4.5** Test with real Telegram bot

## 📊 **Airtable Schema Analysis**

### **Tasks Table (tbl6XreR1ctmQsNJD)**
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| Task | singleLineText | Task title/name | ✅ |
| Details | multilineText | Task description | ✅ |
| Status | singleSelect | To Do, In Progress, Done | ✅ |
| Deadline | date | Due date | ❌ |
| Assigned To | singleLineText | Person responsible | ❌ |
| Created At | date | Creation date | ✅ |
| Notes | multilineText | Additional notes | ❌ |
| Days Until Deadline | formula | Auto-calculated | ✅ |
| Task Summary | aiText | AI-generated summary | ✅ |
| Priority Suggestion | aiText | AI-generated priority | ✅ |

### **Issues Table (tblhmLkzbahZA5Afx)**
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| Reported By | singleLineText | Person reporting | ✅ |
| Category | singleSelect | Equipment, Supply, Complaint, Other | ✅ |
| Description | multilineText | Issue description | ✅ |
| Severity | singleSelect | Low, Medium, High | ✅ |
| Date | date | Report date | ✅ |
| Status | singleSelect | Open, Resolved | ✅ |
| Resolution Notes | multilineText | Resolution details | ❌ |
| Days Open | formula | Auto-calculated | ✅ |
| Issue Summary | aiText | AI-generated summary | ✅ |
| Severity Analysis | aiText | AI-generated analysis | ✅ |

## 🤖 **GPT Prompt Design**

### **Enhanced System Prompt**
```
You are a structured logger for a service station operations system. 

Given a user message, classify it into one of: expense, fuel, task, issue. Extract relevant fields depending on type.

Output JSON with a type field and the appropriate keys:

- expense: date (default today), amount, description, person (default "Me"), receipt_url (if provided)
- fuel: date (default today), vehicle, driver, liters, odometer_start, odometer_end, purpose
- task: task_title, details, status (default "To Do"), deadline (if mentioned), assigned_to (if mentioned)
- issue: category, description, severity (default "Low" if unspecified), status (default "Open"), reported_by (default "Me")

For vehicle selection in fuel logs, use: "Toyota Hilux", "Toyota Prado", or "Other"
For task status, use: "To Do", "In Progress", "Done"
For issue category, use: "Equipment", "Supply", "Complaint", "Other"
For issue severity, use: "Low", "Medium", "High"
For issue status, use: "Open", "Resolved"

For amounts, extract numeric values only (e.g., "15,000 MWK" becomes 15000)
For dates, use YYYY-MM-DD format (today is 2025-08-04)

IMPORTANT: Always include the date field with today's date (2025-08-04) if not specified.
```

### **Example Messages for Training**
```
User: "Need to update project timeline by Friday"
Assistant: {"type": "task", "task_title": "Update project timeline", "details": "Update project timeline", "status": "To Do", "deadline": "2025-08-08", "assigned_to": "Me"}

User: "Equipment malfunction: air compressor not working"
Assistant: {"type": "issue", "category": "Equipment", "description": "Air compressor not working", "severity": "Medium", "status": "Open", "reported_by": "Me"}

User: "Assign John to inspect safety equipment"
Assistant: {"type": "task", "task_title": "Inspect safety equipment", "details": "Inspect safety equipment", "status": "To Do", "assigned_to": "John"}

User: "Fuel supply running low - urgent"
Assistant: {"type": "issue", "category": "Supply", "description": "Fuel supply running low", "severity": "High", "status": "Open", "reported_by": "Me"}
```

## 🔧 **Technical Implementation**

### **1. Update GPT Parser (`api/gpt_parser.py`)**
```python
# Add task and issue examples to get_example_messages()
# Update validation logic for tasks and issues
# Add task and issue confirmation message generators
```

### **2. Update Airtable Client (`api/airtable_client.py`)**
```python
# Add task_fields mapping
task_fields = {
    'task_title': 'Task',
    'details': 'Details', 
    'status': 'Status',
    'deadline': 'Deadline',
    'assigned_to': 'Assigned To',
    'created_at': 'Created At',
    'notes': 'Notes'
}

# Add issue_fields mapping
issue_fields = {
    'reported_by': 'Reported By',
    'category': 'Category',
    'description': 'Description',
    'severity': 'Severity',
    'date': 'Date',
    'status': 'Status',
    'resolution_notes': 'Resolution Notes'
}

# Add create_task() and create_issue() methods
```

### **3. Update Message Processing (`run_bot_polling.py`)**
```python
# Add task and issue handling to process_message_pipeline()
# Update confirmation message generation
# Add task and issue validation
```

## 📱 **User Experience Design**

### **Task Message Examples**
- **"Need to update project timeline by Friday"**
- **"Assign John to inspect safety equipment"**
- **"Prepare client presentation for next week"**
- **"Update website content - deadline Monday"**
- **"Review monthly reports - assign to Sarah"**

### **Issue Message Examples**
- **"Equipment malfunction: air compressor not working"**
- **"Fuel supply running low - urgent"**
- **"Customer complaint about service quality"**
- **"Generator overheating - need immediate attention"**
- **"Unauthorized access to restricted area"**

### **Expected Bot Responses**
```
✅ Task created: "Update project timeline" (Status: To Do, Deadline: 2025-08-08)
✅ Issue logged: "Air compressor malfunction" (Category: Equipment, Severity: Medium)
```

## 🧪 **Testing Strategy**

### **Unit Tests**
- [ ] Test task message parsing
- [ ] Test issue message parsing
- [ ] Test field validation
- [ ] Test Airtable field mapping
- [ ] Test confirmation message generation

### **Integration Tests**
- [ ] Test complete task creation pipeline
- [ ] Test complete issue creation pipeline
- [ ] Test mixed message types
- [ ] Test error handling

### **User Acceptance Tests**
- [ ] Test with real Telegram messages
- [ ] Test edge cases and ambiguous messages
- [ ] Test help command functionality
- [ ] Test error message clarity

## 🚀 **Deployment Plan**

### **Phase 1: Development (Day 1)**
1. Update GPT parser with task/issue examples
2. Extend Airtable client with new field mappings
3. Add task and issue creation methods
4. Update message processing pipeline
5. Test locally with sample messages

### **Phase 2: Testing (Day 2)**
1. Comprehensive testing with various message formats
2. Error handling validation
3. User experience testing
4. Performance testing
5. Documentation updates

### **Phase 3: Production (Day 3)**
1. Deploy updated bot
2. Monitor for any issues
3. Gather user feedback
4. Iterate based on usage patterns

## 📈 **Success Metrics**

### **Technical Metrics**
- [ ] 100% successful parsing of test task messages
- [ ] 100% successful parsing of test issue messages
- [ ] < 5 second response time for all message types
- [ ] 0% data loss or corruption

### **User Experience Metrics**
- [ ] Intuitive message formats
- [ ] Clear confirmation messages
- [ ] Helpful error messages
- [ ] Consistent data quality

### **Operational Metrics**
- [ ] Reduced time to log tasks/issues
- [ ] Improved data consistency
- [ ] Better tracking and accountability
- [ ] Enhanced operational visibility

## 🔄 **Future Enhancements**

### **Short Term (Next Sprint)**
- [ ] Task status updates via bot
- [ ] Issue resolution tracking
- [ ] Deadline reminders
- [ ] Priority notifications

### **Medium Term (Next Month)**
- [ ] Task assignment notifications
- [ ] Issue escalation workflows
- [ ] Reporting and analytics
- [ ] Integration with other systems

### **Long Term (Next Quarter)**
- [ ] Advanced task management
- [ ] Issue tracking and resolution
- [ ] Performance dashboards
- [ ] Mobile app integration

## 📝 **Documentation Updates**

### **User Documentation**
- [ ] Update help command with task/issue examples
- [ ] Create user guide for new features
- [ ] Add troubleshooting section
- [ ] Include best practices

### **Technical Documentation**
- [ ] Update API documentation
- [ ] Document new field mappings
- [ ] Add deployment notes
- [ ] Include testing procedures

## 🎯 **Next Steps**

1. **Start with Phase 1**: Update GPT parser and Airtable client
2. **Implement incrementally**: Test each component thoroughly
3. **Focus on user experience**: Ensure intuitive message formats
4. **Maintain quality**: Comprehensive testing at each stage
5. **Document progress**: Update implementation plan as we go

---

**Estimated Timeline**: 2-3 days for full implementation
**Priority**: High (completes core MVP functionality)
**Dependencies**: Existing bot infrastructure (✅ Complete) 