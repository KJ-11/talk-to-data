// components/FileUpload.js
"use client";
import { useState } from 'react';

const FileUpload = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (res.ok) {
      console.log('File uploaded successfully');
    } else {
      console.error('File upload failed');
    }
  };

  return (
    <div className="container">
      <h1>Upload your file</h1>
      <div className="file-upload">
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={!file}>Upload</button>
      </div>
    </div>
  );
};

export default FileUpload;
