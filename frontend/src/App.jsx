import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // We'll create this for styling

function App() {
  const [recipient, setRecipient] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [enhanceContent, setEnhanceContent] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatusMessage('');
    setIsError(false);

    const payload = {
      destinataire: recipient,
      sujet: subject,
      message: message,
      enhance_content: enhanceContent,
    };

    try {
      // Assuming backend runs on port 5001 based on requirements.txt comment
      const response = await axios.post('http://localhost:5001/message', payload);
      setStatusMessage(`Success: ${response.data.message} (Task ID: ${response.data.task_id})`);
      // Clear form on success
      setRecipient('');
      setSubject('');
      setMessage('');
      setEnhanceContent(false);
    } catch (error) {
      setIsError(true);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setStatusMessage(`Error: ${error.response.data.message || 'Failed to send email.'} (${error.response.status})`);
      } else if (error.request) {
        // The request was made but no response was received
        setStatusMessage('Error: No response from server. Is the backend running?');
      } else {
        // Something happened in setting up the request that triggered an Error
        setStatusMessage(`Error: ${error.message}`);
      }
      console.error("Sending error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Mailer Microservice Frontend</h1>
      <form onSubmit={handleSubmit} className="email-form">
        <div className="form-group">
          <label htmlFor="recipient">Recipient Email:</label>
          <input
            type="email"
            id="recipient"
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="subject">Subject:</label>
          <input
            type="text"
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="message">Message:</label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows="6"
            required
            disabled={isLoading}
          ></textarea>
        </div>
        <div className="form-group enhance-checkbox">
          <input
            type="checkbox"
            id="enhanceContent"
            checked={enhanceContent}
            onChange={(e) => setEnhanceContent(e.target.checked)}
            disabled={isLoading}
          />
          <label htmlFor="enhanceContent">Enhance Content with AI?</label>
        </div>
        <button type="submit" disabled={isLoading} className="submit-button">
          {isLoading ? 'Sending...' : 'Send Email'}
        </button>
      </form>
      {statusMessage && (
        <div className={`status-message ${isError ? 'error' : 'success'}`}>
          {statusMessage}
        </div>
      )}
    </div>
  );
}

export default App;
