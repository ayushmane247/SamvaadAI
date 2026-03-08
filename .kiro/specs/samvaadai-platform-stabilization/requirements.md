# Requirements Document: SamvaadAI Platform Stabilization

## Introduction

SamvaadAI is a voice-first AI platform that helps rural Indian citizens discover government schemes they're eligible for. The system has been implemented with a React + Vite frontend, FastAPI backend with Amazon Bedrock LLM integration, and a deterministic eligibility engine. However, the system is currently unstable and requires comprehensive stabilization to achieve production readiness.

The critical issue is that Bedrock API calls are failing with `AccessDeniedException: INVALID_PAYMENT_INSTRUMENT`, requiring the system to gracefully fallback when AI services are unavailable. This stabilization project will ensure the platform works end-to-end reliably for 5 government schemes with graceful degradation when AI services fail.

## Glossary

- **SamvaadAI_Platform**: The complete voice-first eligibility discovery system
- **Frontend**: React + Vite web application with Web Speech API
- **Backend**: FastAPI application deployed on AWS Lambda
- **Bedrock_Service**: Amazon Bedrock LLM integration for natural language processing
- **Eligibility_Engine**: Deterministic rule-based eligibility evaluator
- **ConversationManager**: Orchestration layer coordinating profile extraction, eligibility evaluation, and response generation
- **ProfileMemory**: Session-based in-memory storage for user profile attributes
- **Session**: Single user interaction with 1-hour TTL, no permanent storage
- **Graceful_Degradation**: System continues functioning with reduced capabilities when services fail
- **Template_Response**: Pre-defined multilingual response patterns used when LLM is unavailable
- **Scheme**: Government program or benefit opportunity
- **PII**: Personally Identifiable Information (must not be stored permanently)

## Requirements

### Requirement 1: Fix Chat API Wiring

**User Story:** As a frontend developer, I want the chat interface to reliably trigger backend API calls, so that user queries are processed correctly.

#### Acceptance Criteria

1. WHEN a user submits a query through the frontend, THE Frontend SHALL send a POST request to `/v1/conversation` endpoint
2. THE Frontend SHALL include the following fields in the request payload: `query` (string), `language` (string), `session_id` (string)
3. WHEN the backend responds, THE Frontend SHALL parse the response according to the backend schema
4. THE Frontend SHALL display the response text to the user within 2 seconds
5. IF the API call fails, THEN THE Frontend SHALL display an error message in the user's selected language
6. THE Frontend SHALL validate that `query` is not empty before sending the request
7. THE Frontend SHALL validate that `language` is one of: "en", "hi", "mr"
8. WHEN a session_id does not exist, THE Frontend SHALL generate a new UUID for the session

### Requirement 2: Implement Smart Profile Memory

**User Story:** As a system architect, I want session-based profile memory, so that user information is accumulated across conversation turns without permanent storage.

#### Acceptance Criteria

1. THE ProfileMemory SHALL store the following fields: occupation, state, income_range, age_group, gender, disability_status, caste_category, farmer_status, student_status
2. WHEN new profile attributes are extracted, THE ProfileMemory SHALL merge non-null values into the existing profile
3. THE ProfileMemory SHALL provide a method to retrieve the complete accumulated profile
4. THE ProfileMemory SHALL provide a method to identify missing required fields
5. THE ProfileMemory SHALL exist only for the session lifetime (1 hour maximum)
6. WHEN a session expires, THE ProfileMemory SHALL be destroyed with no permanent storage
7. THE ProfileMemory SHALL support concurrent sessions with isolated profile data
8. THE ProfileMemory SHALL be thread-safe for concurrent access within a session

### Requirement 3: Optimize Conversation Pipeline with Graceful Fallback

**User Story:** As a system operator, I want the conversation pipeline to work reliably even when Bedrock is unavailable, so that users always receive responses.

#### Acceptance Criteria

1. WHEN a user query is received, THE ConversationManager SHALL extract profile attributes using deterministic rules
2. THE ConversationManager SHALL update ProfileMemory with extracted attributes before calling the Eligibility_Engine
3. THE ConversationManager SHALL evaluate eligibility using the deterministic Eligibility_Engine
4. THE ConversationManager SHALL generate a template response in the user's language
5. IF Bedrock_Service is available AND the template response is less than 150 characters, THEN THE ConversationManager SHALL enhance the response using Bedrock
6. IF Bedrock_Service is unavailable OR returns an error, THEN THE ConversationManager SHALL use the template response without enhancement
7. THE ConversationManager SHALL complete the pipeline within 2 seconds (p95)
8. THE ConversationManager SHALL log whether the response used LLM enhancement or template fallback
9. THE ConversationManager SHALL never use LLM for eligibility decisions (only for language enhancement)
10. WHEN profile extraction fails, THE ConversationManager SHALL use empty profile and request missing information

### Requirement 4: Create Prototype Scheme Dataset

**User Story:** As a content manager, I want exactly 5 government schemes with complete eligibility rules, so that the system can demonstrate end-to-end functionality.

#### Acceptance Criteria

1. THE Scheme_Dataset SHALL include exactly 5 schemes: PM Kisan Samman Nidhi, Ayushman Bharat, PM Awas Yojana, National Scholarship Portal, Pradhan Mantri Mudra Yojana
2. FOR EACH scheme, THE Scheme_Dataset SHALL include: scheme_id, scheme_name, eligibility_criteria, required_documents, benefit_summary, source_url, last_verified_date
3. THE Scheme_Dataset SHALL define eligibility_criteria as a list of rules with field, operator, and value
4. THE Scheme_Dataset SHALL support the following operators: equals, not_equals, less_than, greater_than, between, in, not_in, contains
5. THE Scheme_Dataset SHALL be stored in JSON format in S3 with versioning enabled
6. THE Scheme_Dataset SHALL include official government portal URLs for each scheme
7. THE Scheme_Dataset SHALL include last_verified_date within the past 90 days
8. THE Scheme_Dataset SHALL be loadable by the backend within 500ms during cold start

### Requirement 5: Implement Voice Assistant UX

**User Story:** As a low-literacy user, I want Google Assistant-like voice interactions, so that I can discover schemes without typing.

#### Acceptance Criteria

1. WHEN voice input is active, THE Frontend SHALL display a visual listening indicator
2. THE Frontend SHALL stream response text to the screen as it becomes available
3. THE Frontend SHALL speak the scheme summary using text-to-speech
4. THE Frontend SHALL display clickable scheme cards with scheme name, benefit, and official URL
5. THE Frontend SHALL speak the document checklist for eligible schemes
6. IF speech recognition confidence is less than 0.7, THEN THE Frontend SHALL prompt the user to repeat their input
7. THE Frontend SHALL support voice input in English, Hindi, and Marathi
8. THE Frontend SHALL automatically fallback to text input if voice recognition fails 3 consecutive times
9. THE Frontend SHALL provide a manual toggle between voice and text input modes
10. THE Frontend SHALL display transcribed text for user confirmation before processing

### Requirement 6: Conduct End-to-End Testing

**User Story:** As a QA engineer, I want comprehensive end-to-end test scenarios, so that I can verify the system works correctly.

#### Acceptance Criteria

1. THE System SHALL correctly process the query "I am a farmer from Maharashtra" and extract occupation=farmer, state=Maharashtra
2. THE System SHALL correctly respond to "Which schemes can I apply for?" with eligible schemes based on the accumulated profile
3. THE System SHALL correctly process the query "I am a student from Delhi" and extract occupation=student, state=Delhi
4. THE System SHALL correctly respond to "Any scholarships?" with National Scholarship Portal if the user is a student
5. THE System SHALL provide required document checklists for all eligible schemes
6. THE System SHALL include official government portal URLs in all scheme responses
7. THE System SHALL complete each test conversation within 5 minutes
8. THE System SHALL maintain session state across multiple queries in the same session
9. THE System SHALL work correctly when Bedrock is unavailable (using template responses)
10. THE System SHALL work correctly when Bedrock is available (using enhanced responses)

### Requirement 7: Perform Engineering Audit

**User Story:** As a technical lead, I want a comprehensive engineering audit report, so that I can understand system quality and readiness.

#### Acceptance Criteria

1. THE Audit_Report SHALL document the current system architecture with component diagrams
2. THE Audit_Report SHALL identify system strengths with specific examples
3. THE Audit_Report SHALL identify system weaknesses with severity ratings (critical, high, medium, low)
4. THE Audit_Report SHALL document technical debt with estimated remediation effort
5. THE Audit_Report SHALL assess security posture including authentication, authorization, data protection, and input validation
6. THE Audit_Report SHALL assess AWS deployment readiness including Lambda configuration, API Gateway setup, DynamoDB usage, and S3 integration
7. THE Audit_Report SHALL assess AI integration quality including LLM guardrails, fallback mechanisms, and prompt engineering
8. THE Audit_Report SHALL assess performance characteristics including API latency, eligibility evaluation time, and cold start duration
9. THE Audit_Report SHALL provide quality scores (0-100) for: code quality, test coverage, documentation, security, performance
10. THE Audit_Report SHALL provide prioritized recommendations with implementation effort estimates

### Requirement 8: Ensure Graceful Bedrock Degradation

**User Story:** As a system reliability engineer, I want the system to work without Bedrock, so that payment issues don't cause complete system failure.

#### Acceptance Criteria

1. WHEN Bedrock returns `AccessDeniedException`, THE Backend SHALL log the error and continue with template responses
2. WHEN Bedrock returns any error, THE Backend SHALL not retry more than 3 times with exponential backoff
3. THE Backend SHALL set a 3-second timeout for all Bedrock API calls
4. THE Backend SHALL track Bedrock availability status in memory
5. IF Bedrock fails 5 consecutive times, THEN THE Backend SHALL mark Bedrock as unavailable for 5 minutes
6. THE Backend SHALL provide template responses in English, Hindi, and Marathi
7. THE Backend SHALL include a flag in API responses indicating whether LLM enhancement was used
8. THE Backend SHALL maintain API latency under 500ms (p95) even when Bedrock is unavailable
9. THE Backend SHALL log Bedrock availability metrics to CloudWatch
10. THE Backend SHALL expose a health check endpoint that reports Bedrock status

### Requirement 9: Implement Session Management

**User Story:** As a privacy-conscious developer, I want session-based state management with automatic expiration, so that no PII is stored permanently.

#### Acceptance Criteria

1. WHEN a new conversation starts, THE Backend SHALL create a session with a unique session_id
2. THE Backend SHALL store session data in DynamoDB with a TTL of 1 hour
3. THE Backend SHALL include the following fields in session data: session_id, structured_profile, evaluation_result, conversation_state, created_at, expires_at
4. WHEN a session expires, THE DynamoDB SHALL automatically delete the session data
5. THE Backend SHALL validate that session_id exists before processing subsequent queries
6. IF a session_id is invalid or expired, THEN THE Backend SHALL return an error with status code 404
7. THE Backend SHALL update session data after each conversation turn
8. THE Backend SHALL not store any PII beyond the session lifetime
9. THE Backend SHALL support concurrent sessions with isolated data
10. THE Backend SHALL log session creation and expiration events

### Requirement 10: Implement Deterministic Profile Extraction

**User Story:** As a system architect, I want deterministic profile extraction as a fallback, so that the system works without LLM.

#### Acceptance Criteria

1. THE Profile_Extractor SHALL use keyword matching to extract occupation from user queries
2. THE Profile_Extractor SHALL recognize the following occupations: farmer, student, teacher, doctor, engineer, business owner, unemployed
3. THE Profile_Extractor SHALL use keyword matching to extract state names from user queries
4. THE Profile_Extractor SHALL recognize all 28 Indian states and 8 union territories
5. THE Profile_Extractor SHALL use pattern matching to extract age from queries containing numbers followed by "years", "year", "साल", "वर्ष"
6. THE Profile_Extractor SHALL use pattern matching to extract income from queries containing currency symbols or keywords like "lakh", "thousand", "₹"
7. THE Profile_Extractor SHALL return an empty profile if no attributes can be extracted
8. THE Profile_Extractor SHALL complete extraction within 100ms
9. THE Profile_Extractor SHALL be language-agnostic (work with English, Hindi, Marathi text)
10. THE Profile_Extractor SHALL never call external APIs or LLM services

### Requirement 11: Implement Multilingual Template Responses

**User Story:** As a multilingual user, I want responses in my preferred language, so that I can understand the system without English knowledge.

#### Acceptance Criteria

1. THE Template_Generator SHALL support English, Hindi, and Marathi languages
2. THE Template_Generator SHALL provide templates for the following scenarios: welcome message, missing information request, eligible schemes list, partially eligible schemes list, ineligible schemes list, error message
3. THE Template_Generator SHALL include scheme names, benefits, and document requirements in templates
4. THE Template_Generator SHALL format currency amounts according to Indian numbering system (lakhs, crores)
5. THE Template_Generator SHALL use simple language appropriate for low-literacy users
6. THE Template_Generator SHALL include official portal URLs in scheme templates
7. THE Template_Generator SHALL indicate data freshness using last_verified_date
8. THE Template_Generator SHALL generate responses within 50ms
9. THE Template_Generator SHALL handle missing data gracefully without errors
10. THE Template_Generator SHALL be testable without LLM integration

### Requirement 12: Implement Frontend-Backend Integration

**User Story:** As a full-stack developer, I want seamless frontend-backend integration, so that the user experience is smooth.

#### Acceptance Criteria

1. THE Frontend SHALL send requests to the correct API endpoint based on environment (development: localhost:8000, production: API Gateway URL)
2. THE Frontend SHALL include proper CORS headers in all requests
3. THE Frontend SHALL handle HTTP status codes correctly: 200 (success), 400 (bad request), 404 (not found), 500 (server error)
4. THE Frontend SHALL display loading indicators during API calls
5. THE Frontend SHALL timeout requests after 10 seconds and display an error message
6. THE Frontend SHALL retry failed requests up to 2 times with 1-second delay
7. THE Frontend SHALL validate API responses match the expected schema before rendering
8. THE Frontend SHALL log API errors to browser console for debugging
9. THE Frontend SHALL display user-friendly error messages (not technical stack traces)
10. THE Frontend SHALL maintain session_id across multiple API calls

### Requirement 13: Implement Voice Input Reliability

**User Story:** As a voice user, I want reliable speech recognition, so that my queries are understood correctly.

#### Acceptance Criteria

1. THE Frontend SHALL use Web Speech API for voice input
2. THE Frontend SHALL request microphone permissions before starting voice input
3. IF microphone permission is denied, THEN THE Frontend SHALL fallback to text input and display a message
4. THE Frontend SHALL display real-time transcription as the user speaks
5. THE Frontend SHALL automatically stop listening after 10 seconds of silence
6. THE Frontend SHALL allow manual stop of voice input via a button
7. THE Frontend SHALL handle speech recognition errors gracefully without crashing
8. THE Frontend SHALL support continuous listening mode for multi-turn conversations
9. THE Frontend SHALL indicate speech recognition confidence level to the user
10. IF confidence is below 0.7, THEN THE Frontend SHALL ask for confirmation before processing

### Requirement 14: Implement Scheme Card Display

**User Story:** As a visual user, I want clear scheme cards with actionable information, so that I can understand my options.

#### Acceptance Criteria

1. THE Frontend SHALL display each eligible scheme as a card with: scheme name, eligibility status (eligible/partial), benefit summary, required documents list, official portal link
2. THE Frontend SHALL use color coding: green for eligible, yellow for partially eligible, gray for ineligible
3. THE Frontend SHALL display eligibility status badges prominently on each card
4. THE Frontend SHALL make official portal links clickable and open in new tab
5. THE Frontend SHALL display required documents as a bulleted list
6. THE Frontend SHALL show data freshness indicator (last_verified_date) on each card
7. THE Frontend SHALL display benefit amounts in Indian numbering format (₹2,00,000)
8. THE Frontend SHALL support responsive layout for mobile and desktop
9. THE Frontend SHALL display schemes in priority order: eligible first, then partially eligible, then ineligible
10. THE Frontend SHALL allow users to expand/collapse scheme details

### Requirement 15: Implement Error Handling and Logging

**User Story:** As a DevOps engineer, I want comprehensive error handling and logging, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. THE Backend SHALL log all API requests with: request_id, endpoint, method, status_code, latency_ms
2. THE Backend SHALL log all errors with: error_type, error_message, stack_trace, request_id
3. THE Backend SHALL log Bedrock API calls with: success/failure, latency_ms, error_type
4. THE Backend SHALL log eligibility evaluations with: profile_fields, eligible_count, partial_count, ineligible_count
5. THE Backend SHALL use structured JSON logging for CloudWatch integration
6. THE Backend SHALL not log any PII in production logs
7. THE Backend SHALL assign a unique request_id to each API call for tracing
8. THE Backend SHALL log session lifecycle events: creation, update, expiration
9. THE Backend SHALL log performance metrics: API latency, eligibility evaluation time, LLM response time
10. THE Backend SHALL expose logs to CloudWatch Logs with appropriate log groups

### Requirement 16: Implement Performance Optimization

**User Story:** As a performance engineer, I want the system to meet latency targets, so that users have a responsive experience.

#### Acceptance Criteria

1. THE Backend SHALL respond to API requests within 500ms at p95 percentile
2. THE Eligibility_Engine SHALL evaluate eligibility within 100ms for 10 schemes
3. THE Profile_Extractor SHALL extract profile attributes within 100ms
4. THE Template_Generator SHALL generate responses within 50ms
5. IF Bedrock is used, THE Backend SHALL complete LLM enhancement within 2 seconds
6. THE Backend SHALL preload scheme data during Lambda cold start to reduce latency
7. THE Backend SHALL cache scheme data in memory for the Lambda execution lifetime
8. THE Backend SHALL use connection pooling for DynamoDB and S3 clients
9. THE Backend SHALL implement request timeouts to prevent hanging requests
10. THE Backend SHALL track and log latency metrics for each pipeline stage

### Requirement 17: Implement Security Best Practices

**User Story:** As a security engineer, I want the system to follow security best practices, so that user data is protected.

#### Acceptance Criteria

1. THE Backend SHALL validate all input parameters using Pydantic models
2. THE Backend SHALL sanitize user input to prevent injection attacks
3. THE Backend SHALL use HTTPS for all API communication
4. THE Backend SHALL implement CORS with restricted origins in production
5. THE Backend SHALL implement rate limiting to prevent abuse (100 requests per minute per IP)
6. THE Backend SHALL not expose internal error details in API responses
7. THE Backend SHALL use environment variables for all sensitive configuration
8. THE Backend SHALL not log sensitive data (API keys, session tokens, PII)
9. THE Backend SHALL implement request size limits (max 10KB per request)
10. THE Backend SHALL use AWS IAM roles with least-privilege permissions

### Requirement 18: Create Architecture Diagram

**User Story:** As a technical stakeholder, I want a visual architecture diagram, so that I can understand system components and data flow.

#### Acceptance Criteria

1. THE Architecture_Diagram SHALL show all major components: Frontend, API Gateway, Lambda, DynamoDB, S3, Bedrock
2. THE Architecture_Diagram SHALL show data flow for a complete conversation turn
3. THE Architecture_Diagram SHALL indicate synchronous and asynchronous interactions
4. THE Architecture_Diagram SHALL show the graceful degradation path when Bedrock is unavailable
5. THE Architecture_Diagram SHALL indicate session lifecycle and TTL
6. THE Architecture_Diagram SHALL show the deterministic eligibility evaluation flow
7. THE Architecture_Diagram SHALL use standard notation (boxes for components, arrows for data flow)
8. THE Architecture_Diagram SHALL be exportable as PNG or SVG
9. THE Architecture_Diagram SHALL include a legend explaining symbols and colors
10. THE Architecture_Diagram SHALL be included in the engineering audit report

### Requirement 19: Implement Deployment Readiness

**User Story:** As a deployment engineer, I want the system to be deployment-ready, so that I can deploy to production with confidence.

#### Acceptance Criteria

1. THE Backend SHALL be deployable to AWS Lambda using a deployment script
2. THE Backend SHALL include a requirements.txt with all dependencies pinned to specific versions
3. THE Backend SHALL include environment variable documentation in .env.example
4. THE Backend SHALL include a health check endpoint that validates all dependencies
5. THE Frontend SHALL be deployable to AWS Amplify or S3 + CloudFront
6. THE Frontend SHALL include build scripts for production deployment
7. THE System SHALL include deployment documentation with step-by-step instructions
8. THE System SHALL include rollback procedures in deployment documentation
9. THE System SHALL include monitoring setup instructions for CloudWatch
10. THE System SHALL include a smoke test script to validate deployment

### Requirement 20: Implement Test Coverage

**User Story:** As a quality engineer, I want comprehensive test coverage, so that I can ensure system reliability.

#### Acceptance Criteria

1. THE Backend SHALL have unit tests for all core functions with minimum 80% code coverage
2. THE Backend SHALL have integration tests for API endpoints
3. THE Backend SHALL have tests for Bedrock fallback scenarios
4. THE Backend SHALL have tests for profile extraction with various input formats
5. THE Backend SHALL have tests for eligibility evaluation with all 5 schemes
6. THE Backend SHALL have tests for session management including TTL expiration
7. THE Backend SHALL have tests for multilingual template generation
8. THE Backend SHALL have performance tests validating latency targets
9. THE Backend SHALL have tests that run without external dependencies (mocked)
10. THE Backend SHALL include a test runner script that executes all tests and reports coverage

## Success Metrics

### System Reliability Metrics
- **API Availability**: 99% uptime during testing period
- **Graceful Degradation Success Rate**: 100% of requests succeed when Bedrock is unavailable
- **Error Rate**: Less than 1% of requests result in 5xx errors

### Performance Metrics
- **API Latency (p95)**: Less than 500ms
- **Eligibility Evaluation Time**: Less than 100ms
- **Profile Extraction Time**: Less than 100ms
- **End-to-End Conversation Time**: Less than 5 minutes for complete eligibility discovery

### Functional Metrics
- **Profile Extraction Accuracy**: 90% of profile attributes correctly extracted from test queries
- **Eligibility Evaluation Accuracy**: 100% correct eligibility decisions for test profiles
- **Multilingual Support**: All 3 languages (English, Hindi, Marathi) working correctly
- **Session Management**: 100% of sessions expire correctly after 1 hour

### Quality Metrics
- **Test Coverage**: Minimum 80% code coverage
- **Documentation Completeness**: All components documented with usage examples
- **Security Compliance**: Zero critical or high-severity security issues
- **Code Quality Score**: Minimum 80/100 in engineering audit

### User Experience Metrics
- **Voice Recognition Success Rate**: 80% of voice inputs correctly transcribed
- **Response Clarity**: 90% of template responses understandable by test users
- **Scheme Discovery Success**: 100% of test scenarios result in correct scheme recommendations
- **Document Checklist Completeness**: 100% of eligible schemes include required documents

## Constraints

### Technical Constraints
- System MUST work without Bedrock (graceful degradation is mandatory)
- No permanent PII storage (session-only, 1-hour TTL)
- Voice-first design for low-literacy users
- Multilingual support (English, Hindi, Marathi) is mandatory
- Low-bandwidth optimization (target 50 kbps)
- Deterministic eligibility decisions (AI for language only, never for eligibility)

### Operational Constraints
- Deployment must use existing AWS infrastructure (Lambda, API Gateway, DynamoDB, S3)
- No changes to core eligibility engine logic (already tested and validated)
- Must maintain backward compatibility with existing API contracts
- Must complete stabilization within project timeline

### Compliance Constraints
- Must follow PROJECT_ENGINEERING_RULEBOOK.md standards
- Must maintain EARS pattern compliance in requirements
- Must follow INCOSE quality rules for requirement clarity
- Must not store PII beyond session lifetime (privacy requirement)

## Risks and Assumptions

### Risks
1. **Bedrock Payment Issues**: Bedrock may remain unavailable due to payment instrument issues
   - Mitigation: Implement robust fallback to template responses
2. **Voice Recognition Accuracy**: Web Speech API may have low accuracy for Indian accents
   - Mitigation: Implement confidence thresholds and text fallback
3. **Performance Degradation**: Lambda cold starts may cause latency spikes
   - Mitigation: Implement scheme data preloading and connection pooling
4. **Integration Complexity**: Frontend-backend integration may reveal unexpected issues
   - Mitigation: Comprehensive integration testing and error handling

### Assumptions
1. AWS infrastructure (Lambda, API Gateway, DynamoDB, S3) is available and configured
2. Web Speech API is supported in target browsers (Chrome, Edge, Safari)
3. Users have basic smartphone or computer with internet connectivity
4. Government scheme data is accurate and up-to-date
5. Session-based memory is sufficient (no need for persistent user profiles)
6. Template responses are acceptable when LLM is unavailable
