import React, { useState } from 'react';
import axios from 'axios';

const UploadSchedule = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [technicianId, setTechnicianId] = useState('');
  const [uploadMessage, setUploadMessage] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const handleTechnicianIdChange = (e) => {
    const id = e.target.value;
    setTechnicianId(id);
  };

  const handleUpload = async () => {
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('technician_id', technicianId);

      const response = await axios.post('https://127.0.0.1:5000/upload', formData, {withCredentials: true});

      if (response.status === 200) {
        setUploadMessage(response.data);
      } else {
        setUploadMessage(response.data);
      }
    } catch (error) {
      setUploadMessage('Error: ' + error.message);
    }
  };

  return (
    <div className="excel-upload">
      <input type="file" onChange={handleFileChange} />
      <input
        type="text"
        placeholder="Technician ID"
        value={technicianId}
        onChange={handleTechnicianIdChange}
      />
      <button onClick={handleUpload}>Upload Excel File</button>

      {uploadMessage && (
        <div>
          <p>{uploadMessage}</p>
        </div>
      )}
    </div>
  );
};

export default UploadSchedule;