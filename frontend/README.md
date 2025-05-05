# Mailer Microservice - Frontend

This is a React frontend application for the Mailer Microservice. It provides a user interface to compose and send emails via the backend API.

## Features

*   **Email Composition Form:** Allows users to enter recipient email, subject, and message body.
*   **AI Content Enhancement Option:** Includes a checkbox to request backend AI enhancement (using Gemini) for the email content.
*   **API Integration:** Communicates with the backend service (expected at `http://localhost:5001`) to send email requests.
*   **Status Feedback:** Displays success or error messages received from the backend.
*   **Loading Indicator:** Shows a loading state while the request is being processed.

## Technology Stack

*   **Framework:** React 19
*   **Build Tool:** Vite
*   **HTTP Client:** Axios
*   **Language:** JavaScript (JSX)
*   **Styling:** CSS (`App.css`)
*   **Linting:** ESLint

## Setup

1.  **Prerequisites:**
    *   Node.js and npm (or yarn) installed.
    *   The [Mailer Microservice Backend](<path/to/your/backend/README.md>) must be running and accessible (typically at `http://localhost:5001`).

2.  **Clone Repository:** (If applicable)
    ```bash
    git clone <your-repo-url>
    cd <your-repo-url>/frontend
    ```

3.  **Install Dependencies:**
    Navigate to the `frontend` directory in your terminal and run:
    ```bash
    npm install
    # or if using yarn:
    # yarn install
    ```

## Running the Application

1.  **Start the Development Server:**
    Ensure the backend service is running. Then, in the `frontend` directory, run:
    ```bash
    npm run dev
    # or
    # yarn dev
    ```
    This will start the Vite development server, typically available at `http://localhost:5173` (Vite will usually print the correct URL in the terminal). Open this URL in your web browser.

2.  **Using the Application:**
    *   Fill in the "Recipient Email", "Subject", and "Message" fields.
    *   Optionally, check the "Enhance Content with AI?" box to use the backend's Gemini feature.
    *   Click "Send Email".
    *   Observe the status message below the form for feedback from the backend.

## Available Scripts

In the `frontend` directory, you can run the following scripts:

*   `npm run dev`: Starts the development server with Hot Module Replacement (HMR).
*   `npm run build`: Builds the application for production deployment into the `dist` folder.
*   `npm run lint`: Runs ESLint to check for code style issues.
*   `npm run preview`: Serves the production build locally for previewing.

## Backend Connection

The frontend is configured to connect to the backend API at `http://localhost:5001/message`. If your backend runs on a different address or port, you will need to update the URL in `frontend/src/App.jsx`:

```javascript
// In frontend/src/App.jsx, find this line:
const response = await axios.post('http://localhost:5001/message', payload);
// Change 'http://localhost:5001' if your backend URL is different.
