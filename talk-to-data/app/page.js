// app/page.js
"use client";
import React, { useState } from 'react';

export default function Home() {
  const [selectedDatabase, setSelectedDatabase] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [previewData, setPreviewData] = useState(null);
  const [columns, setColumns] = useState([]);

  const handleDatabaseSelect = (db) => {
    setSelectedDatabase(db);
    // Logic to load columns and preview data for the selected database
  };

  const handleChatSubmit = (message) => {
    // Logic to handle chat submission and response
    setChatHistory([...chatHistory, { message, response: 'Sample response' }]);
  };

  const handleNewDatabase = () => {
    // Logic to open a file upload dialog or form
    alert('New Database button clicked!');
  };

  return (
    <div className="home-container">
      <div className="sidebar">
        <h2>Databases</h2>
        <button className="new-database-btn" onClick={handleNewDatabase}>
          + New Database
        </button>
        <ul>
          {/* Replace with dynamic list of databases/chats */}
          <li onClick={() => handleDatabaseSelect('Database 1')}>Database 1</li>
          <li onClick={() => handleDatabaseSelect('Database 2')}>Database 2</li>
        </ul>
      </div>
      <div className="data-preview">
        <h2>Database Preview</h2>
        <div>
          <h3>Columns</h3>
          <ul>
            {columns.map((col, index) => (
              <li key={index}>{col}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Data</h3>
          <table>
            <thead>
              <tr>
                {columns.map((col, index) => (
                  <th key={index}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewData &&
                previewData.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, i) => (
                      <td key={i}>{value}</td>
                    ))}
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="chat-panel">
        <h2>Chat</h2>
        <div className="chat-history">
          {chatHistory.map((chat, index) => (
            <div key={index}>
              <p><strong>You:</strong> {chat.message}</p>
              <p><strong>Bot:</strong> {chat.response}</p>
            </div>
          ))}
        </div>
        <input
          type="text"
          placeholder="Ask something..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleChatSubmit(e.target.value);
              e.target.value = '';
            }
          }}
        />
      </div>
    </div>
  );
}
