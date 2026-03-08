# Implementation Plan: SamvaadAI Platform Stabilization

## Overview

This implementation plan stabilizes the SamvaadAI voice-first AI platform by connecting the frontend to the backend, implementing graceful Bedrock degradation, creating a prototype scheme dataset, and ensuring end-to-end functionality. The system must work reliably with or without Amazon Bedrock, using template-based fallback responses when AI services are unavailable.

The implementation follows a phased approach: backend stabilization first (graceful degradation, session management, scheme dataset), then frontend integration (API client, voice UX), followed by comprehensive testing and engineering audit.

## Tasks

- [ ] 1. Implement graceful Bedrock degradation and error handling
  - [ ] 1.1 Add Bedrock availability tracking to LLMService
    - Implement module-level `_bedrock_available` flag with timestamp tracking
    - Add logic to mark Bedrock unavailable after 5 consecutive failures
    - Implement 5-minute unavailability period with automatic reset
    - Add `bedrock_available` property to InferenceGateway class
    - _Requirements: 8.4, 8.5, 8.10_
  
  - [ ] 1.2 Implement Bedrock error handling with fallback
    - Add try-except blocks for AccessDeniedException, ThrottlingException, and timeout errors
    - Implement 3-second timeout for all Bedrock API calls
    - Add exponential backoff retry logic (max 3 retries)
    - Log all Bedrock errors with error type and request context
    - Return template response on any Bedrock failure
    - _Requirements: 8.1, 8.2, 8.3, 8.9_
  
  - [ ] 1.3 Add LLM enhancement flag to API responses
    - Add `llm_enhanced` boolean field to ConversationResponse model
    - Set flag to True when Bedrock successfully enhances response
    - Set flag to False when template response is used
    - _Requirements: 8.7_
  
  - [ ] 1.4 Update ConversationManager to use conditional LLM enhancement
    - Check Bedrock availability before attempting enhancement
    - Only enhance if template response < 150 characters
    - Always generate template response first as fallback
    - Ensure pipeline completes within 500ms p95 without Bedrock
    - _Requirements: 3.5, 3.6, 8.8_

- [ ] 2. Create prototype scheme dataset with 5 government schemes
  - [ ] 2.1 Create scheme JSON files for all 5 schemes
    - Create `schemes/pm_kisan.json` with PM Kisan Samman Nidhi data
    - Create `schemes/ayushman_bharat.json` with Ayushman Bharat data
    - Create `schemes/pm_awas_yojana.json` with PM Awas Yojana data
    - Create `schemes/national_scholarship.json` with National Scholarship Portal data
    - Create `schemes/pm_mudra_yojana.json` with Pradhan Mantri Mudra Yojana data
    - Include all required fields: scheme_id, scheme_name, eligibility_criteria, required_documents, benefit_summary, source_url, last_verified_date
    - _Requirements: 4.1, 4.2, 4.6, 4.7_
  
  - [ ] 2.2 Implement eligibility rules for each scheme
    - Define rules using supported operators: equals, not_equals, less_than, greater_than, between, in, not_in, contains
    - Ensure rules reference profile fields: occupation, state, income_range, age_group, gender, disability_status, caste_category, farmer_status, student_status
    - _Requirements: 4.3, 4.4_
  
  - [ ] 2.3 Update SchemeLoader to load schemes from local files
    - Modify `load_schemes()` to read from `schemes/` directory
    - Implement in-memory caching with 300-second TTL
    - Ensure cold start loading completes within 500ms
    - Add error handling for missing or malformed scheme files
    - _Requirements: 4.5, 4.8_

- [ ] 3. Implement deterministic profile extraction
  - [ ] 3.1 Create regex patterns for profile attribute extraction
    - Implement occupation extraction: farmer, student, teacher, doctor, engineer, business owner, unemployed
    - Implement state extraction: all 28 states and 8 union territories (English, Hindi, Marathi names)
    - Implement age extraction: patterns for "years", "year", "साल", "वर्ष"
    - Implement income extraction: patterns for "₹", "lakh", "thousand", currency symbols
    - Implement gender extraction: male/female/other in all languages
    - Implement disability status extraction: disability-related keywords
    - Implement caste category extraction: General, OBC, SC, ST
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_
  
  - [ ] 3.2 Implement profile_extractor function
    - Create `extract_profile(query: str, language: str)` function
    - Apply all regex patterns to extract attributes
    - Return empty profile if no attributes found
    - Ensure execution completes within 100ms
    - Make language-agnostic (work with English, Hindi, Marathi)
    - Never call external APIs or LLM services
    - _Requirements: 10.7, 10.8, 10.9, 10.10_

- [ ] 4. Implement smart profile memory with session management
  - [ ] 4.1 Update ProfileMemory class with all required fields
    - Add fields: occupation, state, income_range, age_group, gender, disability_status, caste_category, farmer_status, student_status
    - Implement merge logic: non-null values overwrite existing values
    - Add `get_missing_fields()` method to identify incomplete profile
    - Add `get_populated_fields()` method to list available data
    - Ensure thread-safe operations for concurrent access
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.8_
  
  - [ ] 4.2 Implement SessionService for DynamoDB persistence
    - Create `create_session()` method returning session_id and timestamps
    - Create `get_session(session_id)` method with validation
    - Create `update_session(session_id, updates)` method
    - Create `delete_session(session_id)` method
    - Set TTL to 3600 seconds (1 hour) on all sessions
    - Store fields: session_id, structured_profile, conversation_state, evaluation_result, ttl, created_at, updated_at
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.7_
  
  - [ ] 4.3 Add session lifecycle logging
    - Log session creation with session_id and created_at
    - Log session updates with session_id and updated fields
    - Log session expiration events
    - Ensure no PII is logged in production
    - _Requirements: 9.8, 9.10, 15.6_
  
  - [ ] 4.4 Update ConversationManager to use SessionService
    - Load session at start of each conversation turn
    - Update ProfileMemory from session data
    - Save updated profile and evaluation result to session after processing
    - Return 404 error if session_id is invalid or expired
    - _Requirements: 9.5, 9.6, 2.5, 2.6, 2.7_

- [ ] 5. Implement multilingual template responses
  - [ ] 5.1 Create template functions for all scenarios
    - Implement welcome message template (no profile data)
    - Implement missing information request template (incomplete profile)
    - Implement eligible schemes list template (with benefits and URLs)
    - Implement partially eligible schemes list template (with guidance)
    - Implement ineligible schemes list template (with reasons)
    - Implement error message template (system failures)
    - _Requirements: 11.2_
  
  - [ ] 5.2 Add multilingual support for English, Hindi, and Marathi
    - Create language-specific templates for each scenario
    - Use simple language appropriate for low-literacy users
    - Format currency using Indian numbering system (lakhs, crores)
    - Include scheme names, benefits, and document requirements
    - Include official portal URLs in scheme templates
    - _Requirements: 11.1, 11.3, 11.4, 11.5, 11.6_
  
  - [ ] 5.3 Implement TemplateGenerator class
    - Create `build_template_response(eligibility, missing_fields, language)` function
    - Handle missing data gracefully without errors
    - Ensure execution completes within 50ms
    - Make testable without LLM integration
    - _Requirements: 11.7, 11.8, 11.9, 11.10_

- [ ] 6. Optimize conversation pipeline performance
  - [ ] 6.1 Add performance tracking to ConversationManager
    - Track latency for each pipeline stage: extraction, memory update, evaluation, template generation, LLM enhancement
    - Log performance metrics with request_id for tracing
    - Ensure total latency < 500ms p95 without Bedrock
    - Ensure total latency < 2000ms p95 with Bedrock
    - _Requirements: 16.1, 16.5, 16.10_
  
  - [ ] 6.2 Optimize SchemeLoader with caching
    - Preload scheme data during Lambda cold start
    - Cache scheme data in memory for Lambda execution lifetime
    - Implement connection pooling for S3 client
    - _Requirements: 16.6, 16.7, 16.8_
  
  - [ ] 6.3 Add request timeouts to prevent hanging
    - Set 3-second timeout for Bedrock calls
    - Set 10-second timeout for DynamoDB operations
    - Set 5-second timeout for S3 operations
    - _Requirements: 16.9_

- [ ] 7. Implement frontend API client
  - [ ] 7.1 Create APIClient class in frontend/src/services/api.js
    - Implement `startSession()` method calling POST /v1/session/start
    - Implement `sendQuery(request)` method calling POST /v1/conversation
    - Implement `checkHealth()` method calling GET /health
    - Configure base URL: localhost:8000 (dev), API Gateway URL (prod)
    - _Requirements: 12.1, 1.1_
  
  - [ ] 7.2 Add request validation and error handling
    - Validate query is not empty before sending
    - Validate language is one of: "en", "hi", "mr"
    - Generate new UUID for session_id if not exists
    - Handle HTTP status codes: 200, 400, 404, 500
    - Display user-friendly error messages in selected language
    - _Requirements: 1.6, 1.7, 1.8, 12.3, 12.9_
  
  - [ ] 7.3 Implement retry logic and timeouts
    - Set 10-second timeout for all requests
    - Retry failed requests up to 2 times with 1-second delay
    - Display loading indicators during API calls
    - Log API errors to browser console
    - _Requirements: 12.5, 12.6, 12.8_
  
  - [ ] 7.4 Add response validation and session management
    - Validate API responses match expected schema before rendering
    - Maintain session_id across multiple API calls
    - Include proper CORS headers in all requests
    - _Requirements: 12.7, 12.10, 12.2_

- [ ] 8. Implement voice assistant UX
  - [ ] 8.1 Create VoiceInput component
    - Implement Web Speech API integration using SpeechRecognition
    - Support languages: English (en-IN), Hindi (hi-IN), Marathi (mr-IN)
    - Display visual listening indicator when active
    - Display real-time transcription as user speaks
    - Auto-stop after 10 seconds of silence
    - Allow manual stop via button
    - _Requirements: 13.1, 13.4, 13.5, 13.6, 5.1, 5.7_
  
  - [ ] 8.2 Add voice input reliability features
    - Request microphone permissions before starting
    - Fallback to text input if permission denied
    - Handle speech recognition errors gracefully
    - Support continuous listening mode for multi-turn conversations
    - Display confidence level indicator
    - Ask for confirmation if confidence < 0.7
    - Fallback to text input after 3 consecutive failures
    - _Requirements: 13.2, 13.3, 13.7, 13.8, 13.9, 13.10, 5.6, 5.8_
  
  - [ ] 8.3 Create VoiceOutput component
    - Implement Web Speech API integration using SpeechSynthesis
    - Select language-appropriate voices
    - Set rate to 0.9 for clarity
    - Speak scheme summaries using TTS
    - Speak document checklists for eligible schemes
    - _Requirements: 5.3, 5.5_
  
  - [ ] 8.4 Add voice/text mode toggle
    - Provide manual toggle between voice and text input
    - Display transcribed text for user confirmation
    - _Requirements: 5.9, 5.10_

- [ ] 9. Implement scheme card display
  - [ ] 9.1 Create SchemeCard component
    - Display scheme name, eligibility status, benefit summary, required documents, official URL
    - Use color coding: green (eligible), yellow (partial), gray (ineligible)
    - Display status badge prominently at top
    - Make official portal links clickable (open in new tab)
    - Display required documents as bulleted list
    - Show data freshness indicator (last_verified_date)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_
  
  - [ ] 9.2 Add responsive layout and interactions
    - Format benefit amounts in Indian numbering (₹2,00,000)
    - Support responsive layout for mobile and desktop
    - Display schemes in priority order: eligible, partial, ineligible
    - Allow expand/collapse of scheme details
    - _Requirements: 14.7, 14.8, 14.9, 14.10_

- [ ] 10. Wire frontend chat interface to backend
  - [ ] 10.1 Update Chat component to use APIClient
    - Replace hardcoded questions with backend API calls
    - Call `startSession()` on component mount
    - Call `sendQuery()` when user submits query
    - Parse and display response from backend
    - Display response text within 2 seconds
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ] 10.2 Update Results component to use backend data
    - Remove local eligibility calculation logic
    - Display eligibility results from backend response
    - Render SchemeCard components for each scheme
    - Display required documents from backend response
    - _Requirements: 1.3_

- [ ] 11. Implement comprehensive error handling and logging
  - [ ] 11.1 Add structured logging to backend
    - Log all API requests with: request_id, endpoint, method, status_code, latency_ms
    - Log all errors with: error_type, error_message, stack_trace, request_id
    - Log Bedrock API calls with: success/failure, latency_ms, error_type
    - Log eligibility evaluations with: profile_fields, eligible_count, partial_count, ineligible_count
    - Use structured JSON logging for CloudWatch integration
    - Assign unique request_id to each API call
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.7_
  
  - [ ] 11.2 Add CloudWatch integration
    - Configure CloudWatch Logs with appropriate log groups
    - Expose logs to CloudWatch with structured format
    - _Requirements: 15.10_

- [ ] 12. Implement security best practices
  - [ ] 12.1 Add input validation and sanitization
    - Validate all input parameters using Pydantic models
    - Sanitize user input to prevent injection attacks
    - Implement request size limits (max 10KB per request)
    - _Requirements: 17.1, 17.2, 17.9_
  
  - [ ] 12.2 Configure CORS and rate limiting
    - Implement CORS with restricted origins in production
    - Implement rate limiting (100 requests per minute per IP)
    - _Requirements: 17.4, 17.5_
  
  - [ ] 12.3 Secure configuration and error handling
    - Use HTTPS for all API communication
    - Use environment variables for all sensitive configuration
    - Do not expose internal error details in API responses
    - Do not log sensitive data (API keys, session tokens, PII)
    - Use AWS IAM roles with least-privilege permissions
    - _Requirements: 17.3, 17.6, 17.7, 17.8, 17.10_

- [ ] 13. Checkpoint - Ensure backend and frontend integration works
  - Manually test complete conversation flow from frontend to backend
  - Verify session management works correctly
  - Verify graceful Bedrock degradation works
  - Verify all 5 schemes are loaded and evaluated correctly
  - Ensure all tests pass, ask the user if questions arise

- [ ]* 14. Write comprehensive backend unit tests
  - [ ]* 14.1 Write tests for ProfileExtractor
    - Test occupation extraction for all supported occupations
    - Test state extraction for all states and union territories
    - Test age extraction with various formats
    - Test income extraction with various formats
    - Test extraction in English, Hindi, and Marathi
    - Test empty profile return when no attributes found
    - Validate execution time < 100ms
    - _Requirements: 20.4_
  
  - [ ]* 14.2 Write tests for EligibilityEngine
    - Test eligibility evaluation for all 5 schemes
    - Test all operators: equals, not_equals, less_than, greater_than, between, in, not_in, contains
    - Test partial eligibility scenarios
    - Test full eligibility scenarios
    - Test ineligible scenarios
    - Validate execution time < 100ms
    - _Requirements: 20.5_
  
  - [ ]* 14.3 Write tests for TemplateGenerator
    - Test template generation for all scenarios
    - Test multilingual templates (English, Hindi, Marathi)
    - Test currency formatting
    - Test missing data handling
    - Validate execution time < 50ms
    - _Requirements: 20.7_
  
  - [ ]* 14.4 Write tests for SessionService
    - Test session creation with TTL
    - Test session retrieval
    - Test session update
    - Test session deletion
    - Test invalid session_id handling
    - Test TTL expiration behavior
    - _Requirements: 20.6_
  
  - [ ]* 14.5 Write tests for Bedrock fallback
    - Test AccessDeniedException handling
    - Test ThrottlingException handling
    - Test timeout handling
    - Test availability tracking (5 consecutive failures)
    - Test 5-minute unavailability period
    - Test template fallback when Bedrock unavailable
    - _Requirements: 20.3_
  
  - [ ]* 14.6 Write API endpoint integration tests
    - Test POST /v1/conversation endpoint
    - Test POST /v1/session/start endpoint
    - Test GET /health endpoint
    - Test error responses (400, 404, 500)
    - Test request validation
    - _Requirements: 20.2_
  
  - [ ]* 14.7 Write performance tests
    - Test API latency < 500ms p95 without Bedrock
    - Test API latency < 2000ms p95 with Bedrock
    - Test eligibility evaluation < 100ms
    - Test profile extraction < 100ms
    - Test template generation < 50ms
    - _Requirements: 20.8_
  
  - [ ]* 14.8 Configure test runner and coverage reporting
    - Create test runner script that executes all tests
    - Configure coverage reporting with minimum 80% threshold
    - Ensure tests run without external dependencies (mocked)
    - _Requirements: 20.1, 20.9, 20.10_

- [ ]* 15. Write end-to-end test scenarios
  - [ ]* 15.1 Test farmer eligibility scenario
    - Test query: "I am a farmer from Maharashtra"
    - Verify occupation=farmer, state=Maharashtra extracted
    - Test query: "Which schemes can I apply for?"
    - Verify PM Kisan Samman Nidhi is eligible
    - Verify required documents are provided
    - Verify official URL is included
    - _Requirements: 6.1, 6.2, 6.5, 6.6_
  
  - [ ]* 15.2 Test student scholarship scenario
    - Test query: "I am a student from Delhi"
    - Verify occupation=student, state=Delhi extracted
    - Test query: "Any scholarships?"
    - Verify National Scholarship Portal is eligible
    - Verify required documents are provided
    - Verify official URL is included
    - _Requirements: 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 15.3 Test session state persistence
    - Start new session
    - Send multiple queries in same session
    - Verify profile accumulates across queries
    - Verify session_id is maintained
    - Verify conversation completes within 5 minutes
    - _Requirements: 6.7, 6.8_
  
  - [ ]* 15.4 Test graceful degradation scenarios
    - Test with Bedrock unavailable (mock AccessDeniedException)
    - Verify system uses template responses
    - Verify llm_enhanced flag is False
    - Test with Bedrock available
    - Verify system uses enhanced responses when appropriate
    - Verify llm_enhanced flag is True
    - _Requirements: 6.9, 6.10_

- [ ] 16. Perform engineering audit
  - [ ] 16.1 Document current system architecture
    - Create architecture diagram showing all components
    - Show data flow for complete conversation turn
    - Show graceful degradation path
    - Show session lifecycle and TTL
    - Include legend explaining symbols and colors
    - Export as PNG or SVG
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9_
  
  - [ ] 16.2 Assess system strengths and weaknesses
    - Identify system strengths with specific examples
    - Identify system weaknesses with severity ratings (critical, high, medium, low)
    - Document technical debt with estimated remediation effort
    - _Requirements: 7.2, 7.3, 7.4_
  
  - [ ] 16.3 Assess security, deployment, AI integration, and performance
    - Assess security posture: authentication, authorization, data protection, input validation
    - Assess AWS deployment readiness: Lambda, API Gateway, DynamoDB, S3
    - Assess AI integration quality: LLM guardrails, fallback mechanisms, prompt engineering
    - Assess performance characteristics: API latency, eligibility evaluation time, cold start duration
    - _Requirements: 7.5, 7.6, 7.7, 7.8_
  
  - [ ] 16.4 Generate quality scores and recommendations
    - Provide quality scores (0-100) for: code quality, test coverage, documentation, security, performance
    - Provide prioritized recommendations with implementation effort estimates
    - Include architecture diagram in audit report
    - _Requirements: 7.9, 7.10, 18.10_

- [ ] 17. Prepare deployment readiness
  - [ ] 17.1 Create Lambda deployment script
    - Create deployment script for AWS Lambda
    - Pin all dependencies in requirements.txt to specific versions
    - Create .env.example with environment variable documentation
    - _Requirements: 19.1, 19.2, 19.3_
  
  - [ ] 17.2 Create health check endpoint
    - Implement GET /health endpoint
    - Validate all dependencies (DynamoDB, S3, Bedrock)
    - Return status, version, and bedrock_available flag
    - _Requirements: 19.4, 8.10_
  
  - [ ] 17.3 Create deployment documentation
    - Write step-by-step deployment instructions
    - Document rollback procedures
    - Document monitoring setup for CloudWatch
    - Create smoke test script to validate deployment
    - _Requirements: 19.7, 19.8, 19.9, 19.10_
  
  - [ ] 17.4 Prepare frontend deployment
    - Create build scripts for production deployment
    - Configure deployment to AWS Amplify or S3 + CloudFront
    - _Requirements: 19.5, 19.6_

- [ ] 18. Final checkpoint - Validate complete system
  - Run all unit tests and verify 80% coverage
  - Run all integration tests and verify passing
  - Run end-to-end test scenarios and verify correct behavior
  - Verify graceful Bedrock degradation works in all scenarios
  - Verify performance targets met (API latency < 500ms p95)
  - Verify security best practices implemented
  - Review engineering audit report
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at critical milestones
- Backend stabilization (tasks 1-6) should be completed before frontend integration (tasks 7-10)
- Testing tasks (14-15) validate all functionality comprehensively
- Engineering audit (task 16) provides quality assessment and recommendations
- Deployment readiness (task 17) ensures production deployment capability
