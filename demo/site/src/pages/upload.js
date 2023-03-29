import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [videoSelected, setVideoSelected] = useState('video2');
  const [responseText, setResponseText] = useState('');
  const [jobData, setJobData] = useState('');

  const videos = {
    video1: {
      url:
        'https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4',
    },
    video2: {
      url:
        'https://storage.googleapis.com/sieve-public-videos/celebrity-videos/obama_interview.mp4',
    },
    video3: {
      url:
        'https://storage.googleapis.com/sieve-public-videos/celebrity-videos/elon_podcast.mp4',
    },
  };

  const handleVideoChange = (e) => {
    setVideoSelected(e.target.value);
  };

  const getJobStatus = async (jobId) => {
    const url = `https://mango.sievedata.com/v1/jobs/${jobId}`;
    const headers = {
      'X-API-Key': 'redacted',
    };

    try {
      const response = await axios.get(url, { headers });
      const status = response.data.status;

      if (status === 'finished') {
        setJobData(response.data.data);
      } else {
        setTimeout(() => {
          getJobStatus(jobId);
        }, 1000); // Poll every 1 second
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const inputs = {
      video: videos[videoSelected],
      name: videoSelected,
      user_id: 'ishan0102',
    };

    const url = 'https://mango.sievedata.com/v1/push';
    const body = { workflow_name: 'copilot_upload', inputs };
    const headers = {
      'X-API-Key': 'redacted',
      'Content-Type': 'application/json',
    };

    try {
      const response = await axios.post(url, body, { headers });
      setResponseText(response.data);
      getJobStatus(response.data.id);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-5">
      <h1 className="text-4xl font-bold mb-5">Upload Workflow</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <select
          value={videoSelected}
          onChange={handleVideoChange}
          className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        >
          <option value="video1">Dwyane Basketball</option>
          <option value="video2">Obama Interview</option>
          <option value="video3">Elon Podcast</option>
        </select>
        <button
          type="submit"
          className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
        >
          Upload
        </button>
      </form>
      {responseText && (
        <div className="mt-8 w-full max-w-xl p-6 bg-white rounded shadow-md">
          <h2 className="text-2xl font-bold mb-4">Response:</h2>
          <pre className="whitespace-pre-wrap break-all">
            {JSON.stringify(responseText, null, 2)}
          </pre>
        </div>
      )}

      {jobData && (
        <div className="mt-8 w-full max-w-xl p-6 bg-white rounded shadow-md">
          <h2 className="text-2xl font-bold mb-4">Data:</h2>
          <pre
            className="whitespace-pre-wrap break-all h-64 overflow-y-scroll border border-gray-200 rounded p-4"
          >
            {JSON.stringify(jobData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
