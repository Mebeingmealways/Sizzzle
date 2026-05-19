# Backend API Test Cases

Format used for each case:
- API being tested
- Inputs
- Expected output
- Actual output
- Result (Success/Fail)

## Authentication APIs

1. API being tested: `POST /api/auth/register`
Inputs: Valid customer payload with unique email.
Expected output: `201` with created user, and token or verification-required response.
Actual output: `201` response with expected registration payload shape.
Result: Success.

2. API being tested: `POST /api/auth/register`
Inputs: Duplicate email.
Expected output: `409` conflict-style error response.
Actual output: Duplicate registration rejected with error response.
Result: Success.

3. API being tested: `POST /api/auth/login`
Inputs: Valid user credentials.
Expected output: `200` with JWT token and user object.
Actual output: `200` with token and profile data.
Result: Success.

4. API being tested: `POST /api/auth/login`
Inputs: Invalid password for existing email.
Expected output: `401` unauthorized error.
Actual output: Unauthorized error returned.
Result: Success.

5. API being tested: `POST /api/auth/forgot-password`
Inputs: Existing email.
Expected output: Generic success response (no account enumeration leak).
Actual output: Generic success response returned.
Result: Success.

## Profile APIs

6. API being tested: `GET /api/auth/me`
Inputs: Valid bearer token.
Expected output: `200` with authenticated user profile.
Actual output: Profile payload returned successfully.
Result: Success.

7. API being tested: `PUT /api/profile`
Inputs: Valid profile update payload.
Expected output: `200` with updated profile details.
Actual output: Profile updates persisted and returned.
Result: Success.

8. API being tested: `PUT /api/profile/taste`
Inputs: Valid taste profile payload.
Expected output: `200` with updated taste preferences.
Actual output: Taste profile saved and returned.
Result: Success.

## Booking APIs

9. API being tested: `POST /api/bookings`
Inputs: Authenticated customer and valid booking data.
Expected output: `201` with booking object and code.
Actual output: Booking created successfully.
Result: Success.

10. API being tested: `GET /api/bookings`
Inputs: Authenticated customer token.
Expected output: `200` with bookings list for customer.
Actual output: Customer bookings returned.
Result: Success.

11. API being tested: `POST /api/bookings/{id}/cancel`
Inputs: Valid booking id and cancellable state.
Expected output: `200` with cancelled booking and cancellation charge.
Actual output: Cancellation completed and charge reported.
Result: Success.

12. API being tested: `POST /api/bookings/{id}/rate`
Inputs: Completed booking id and rating payload.
Expected output: `200` review created.
Actual output: Review saved successfully.
Result: Success.

## Manager and Admin APIs

13. API being tested: `GET /api/manager/verification-queue`
Inputs: Manager token.
Expected output: `200` queue payload.
Actual output: Queue data returned.
Result: Success.

14. API being tested: `POST /api/manager/verify-cook/{id}`
Inputs: Manager token and verification action payload.
Expected output: `200` with updated verification state.
Actual output: Verification action applied correctly.
Result: Success.

15. API being tested: `GET /api/admin/stats`
Inputs: Admin token.
Expected output: `200` with platform metrics.
Actual output: Metrics returned as expected.
Result: Success.

16. API being tested: `PUT /api/admin/policies/{id}`
Inputs: Admin token and policy update payload.
Expected output: `200` with updated policy.
Actual output: Policy update persisted.
Result: Success.

## Test Execution Evidence

- Backend pytest execution completed successfully for the core backend suite.
- Latest local run result: 23 passed.
