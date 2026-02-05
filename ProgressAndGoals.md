# Progress and Goals (Refined Version)

## 1. Completed Work and Requirements Met

### Backend Development

- **RESTful API Server for Geographic Data**
  - Implemented a RESTful API server to manage countries, states, and cities.
  - Requirements met: API endpoints for all core entities, RESTful conventions, scalable and clear URL structures.
- **CRUD Operations**
  - Full Create, Read, Update, and Delete support for all data models.
  - Requirements met: Each resource supports GET, POST, PUT/PATCH, DELETE; input validation and error handling ensure data integrity.
- **API Endpoints**
  - Over a dozen endpoints created for all required data interactions.
  - Requirements met: Endpoints map clearly to resources and actions, designed for scalability.
- **Testing and Documentation**
  - Unit tests for endpoints and backend logic using pytest.
  - API documented with Swagger/OpenAPI (request parameters, schemas, status codes).
  - Requirements met: Reliable, testable backend; comprehensive documentation for development and integration.
- **In-Memory Caching**
  - RAM-based caching for frequently accessed data.
  - Requirements met: Improved performance, reduced redundant DB operations.
- **Deployment and CI/CD**
  - Initial CI/CD pipeline (GitHub Actions) and cloud deployment (Heroku) configured.
  - Requirements met: Automated deployment, cloud readiness, partial production deployment.
  - Some connectivity and configuration issues remain, which are currently preventing a fully stable production deployment.

## 2. Goals for This Semester

### Overall Approach

- **Goal:** Finalize backend, improve code structure, and deliver a user-friendly frontend.
- **Requirement:** Stable, maintainable, and scalable application ready for user interaction and future growth.
- **How:** Refactor the code for separation of concerns, decouple files, ensure clear communication across the team and have detailed documentation.

### Backend Goals

- **Stabilize Cloud Deployment**
  - Requirement: Fully stable, cloud-hosted API server with secure configuration.
  - How: Resolve CI/CD and connectivity issues, configure environment variables and secrets, monitor deployment.
- **Maintain and Improve Code Quality**
  - Requirement: High-quality, maintainable, and reliable backend code.
  - How: Expand unit test coverage (edge cases, error scenarios), refactor for modularity, optimize caching.

### Frontend Goals

- **Frontend–API Integration**
  - Requirement: Users can interact with all core data models via the UI.
  - How: Develop a React frontend that connects to the API, supports CRUD for countries, states, and cities, and reflects real-time data changes. Ensure all frontend actions trigger appropriate API requests and update the UI accordingly.

- **Interactive “Spin the Globe” Experience**
- Requirement: Provide an engaging way for users to explore geographic data.
  How:
    - Implement a 3D or animated spinning globe/map interface as the primary entry point to the application.
    - There will be a button for users to select the country, state, and city.
    - Users can spin, zoom, and click on regions or countries on the globe.
    - Selecting a country on the globe loads its detailed information from the API, including associated states and cities
    - The globe view acts as both a visualization tool and a navigation mechanism into deeper data views.

- **Detailed Feature Set and User Interactions**
  - Requirement: Comprehensive, intuitive, and accessible user experience.
  - How:
    - **Entity Pages:** Dedicated pages for countries, states, and cities, each with list and detail views.
    - **CRUD Operations:**
      - Users can add, edit, and delete countries, states, and cities through modal or inline forms.
      - All forms include client-side validation (required fields, data types, etc.) and display clear error messages for invalid input.
      - Success and error feedback is provided via toasts, modals, or inline messages.
    - **Search and Filter:**
      - Users can search and filter lists by name or other attributes.
      - Filtered results update in real time as users type or select filters.
    - **Navigation:**
      - Intuitive navigation structure (sidebar, top bar, or breadcrumbs) for moving between entity pages and detail views.
      - Support for deep linking and browser navigation (back/forward).
    - **Loading and Data Refresh:**
      - Loading indicators are shown during data fetches or updates.
      - Data refreshes automatically after CRUD actions, ensuring the UI always reflects the latest state.

- **Usability Testing and Iteration**
  - Requirement: User-friendly and effective UI.
  - How: Conduct usability testing with real users or peers to identify confusing workflows or missing features. Gather feedback and iterate on UI design, navigation, and API usage to improve the overall experience.

## 3. Technology Stack

- **Main Language:** Python 3.9 or greater
- **OS:** UNIX-like (MacOS, Linux, WSL, etc.)
- **Testing:** pytest
- **API server:** Flask and Flask-RESTX
- **Database:** MongoDB
- **Build:** make
- **Lint:** flake8
- **CI/CD:** GitHub Actions
- **Cloud deployment:** Heroku
- **Frontend:** React
- **Project management:** Kanban board on GitHub

---

**Next Steps:**

- Continue backend and deployment refinement
- Begin frontend development and integration
- Update this document and the README as progress is made
