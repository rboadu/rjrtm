# Progress and Goals

## Completed Requirements

#### Backend Development
- RESTful API Server for Geographic Data
  Successfully implemented a RESTful API server to manage geographic data, including countries, states, and cities.  
  - All required endpoints are functional and integrated.
  - Endpoints follow RESTful conventions and consistent URL structures.

- CRUD Operations   
  Implemented full Create, Read, Update, and Delete (CRUD) functionality for all core data models.  
  - Each resource supports appropriate HTTP methods (GET, POST, PUT/PATCH, DELETE).
  - Input validation and error handling are implemented to ensure data integrity.

-  API Endpoints   
  Created over a dozen endpoints to support all required data interactions.  
  - Endpoints are designed for scalability and clarity.
  - Each endpoint maps clearly to a specific resource and action.

-  Testing and Documentation   
  - Unit tests have been written for endpoints and supporting backend functions to ensure correctness and reliability.
  - All endpoints are documented using Swagger, including:
    - Request parameters
    - Request/response schemas
    - HTTP status codes
  - This documentation supports both development and future client-side integration.

-  In-Memory Caching   
   - Implemented RAM-based caching where practical to optimize performance for frequently accessed data and reduce redundant database operations.

#### Deployment and CI/CD
-  Cloud Deployment (Partially Completed)   
  An initial CI/CD pipeline has been configured to automate deployment.
  - The API server has been prepared for cloud hosting.
  - Some connectivity and configuration issues remain, which are currently preventing a fully stable production deployment.

### Technology Stack
-  Backend: Node.js, Express  
-  Database: Geographic dataset(structured collections for countries, states, and cities)  
-  API Documentation: Swagger(OpenAPI)  
-  Testing: Unit tests for endpoints and backend logic  
-  Deployment: Cloud hosting with CI/CD pipeline integration  

### Goals for the Semester

#### Overall Approach
This semester, our approach is to first stabilize and finalize the backend infrastructure.
We plan on improving the file structure to have proper seperation of concerns. We also plan to decouple files. The endpoints will no longer be in one file and seperated. We'll look into potentially adding or revising endpoints to make sure the full backend functionality meets the needs of the frontend. After finalizing the backend, we'll focus on frontend integration and user-facing functionality. We plan to have a page for each entity, ex: country will have it's own page. We'll achieve it by splitting up the work evenly. The front-end design and functionality is likely to change and grow as we go a long the way, so we'll aim for proper communication, comprehensive documentation, and equal work division to help us achieve a user friendly frontend. 


#### Backend Goals
-  Stabilize Cloud Deployment 
  - Resolve remaining CI/CD configuration and connectivity issues.
  - Achieve a stable cloud-hosted deployment of the API server.
  - Ensure environment variables, secrets, and networking are properly configured.

-  Maintain and Improve Code Quality 
  - Expand unit test coverage to include edge cases.
  - Refactor backend code for improved readability, modularity, and maintainability.
  - Monitor performance and optimize caching strategies where needed.


#### Frontend Goals
-  Frontend–API Integration 
  - Develop a frontend or client interface that connects directly to the API.
  - Implement features that allow users to:
    - View lists of countries, states, and cities
    - Retrieve detailed information for specific locations
    - Create, update, and delete records through the UI
  - Ensure frontend actions correctly trigger API requests and reflect real-time data changes.

-  User Interaction and Behavior 
  - Design intuitive navigation for exploring geographic data.
  - Provide clear feedback for user actions (loading states, success messages, error handling).
  - Ensure forms validate input before sending requests to the API.

-  Usability Testing 
  - Conduct basic usability testing to identify confusing workflows or missing features.
  - Iterate on UI design and API usage based on feedback to improve overall user experience.
