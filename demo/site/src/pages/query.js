import { useState } from 'react';
import axios from 'axios';

export default function Query() {
  const [responseText, setResponseText] = useState('');
  const [jobData, setJobData] = useState('');

  const videos = [
    {
      url:
        'https://storage.googleapis.com/sieve-public-videos/celebrity-videos/dwyane_basketball.mp4',
    },
    {
      url:
        'https://storage.googleapis.com/sieve-public-videos/celebrity-videos/obama_interview.mp4',
    },
    {
      url:
        'https://storage.googleapis.com/sieve-public-videos/celebrity-videos/elon_podcast.mp4',
    },
  ];

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

  const [instructions, setInstructions] = useState('');
  const [videoInputs, setVideoInputs] = useState([
    { url: '', id: 0 },
    { url: '', id: 1 },
  ]);

  const handleInputChange = (e, index) => {
    const { name, value } = e.target;
    const list = [...videoInputs];
    list[index][name] = value;
    setVideoInputs(list);
  };

  const handleInstructionsChange = (e) => {
    setInstructions(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Filter out empty video URLs
    const filteredVideos = videoInputs.filter((input) => input.url.trim() !== '');

    const inputs = {
      videos: filteredVideos,
      instructions,
      user_id: 'ishan0102',
    };

    const url = 'https://mango.sievedata.com/v1/push';
    const body = { workflow_name: 'copilot_query', inputs };
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
      {/* ... */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-4">
          {videoInputs.map((input, index) => (
            <div key={input.id} className="w-full">
              <label
                htmlFor={`video${input.id}`}
                className="block text-sm font-medium text-gray-700"
              >
                Video {index + 1} URL
              </label>
              <input
                id={`video${input.id}`}
                name="url"
                type="url"
                value={input.url}
                onChange={(e) => handleInputChange(e, index)}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
          ))}
          <div className="w-full">
            <label htmlFor="instructions" className="block text-sm font-medium text-gray-700">
              Instructions
            </label>
            <textarea
              id="instructions"
              name="instructions"
              value={instructions}
              onChange={handleInstructionsChange}
              rows={3}
              className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            ></textarea>
          </div>
        </div>
        <button
          type="submit"
          className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
        >
          Run Query Workflow
        </button>
      </form>
      {responseText && (
        <div className="mt-8 w-full max-w-xl p-6 bg-white rounded shadow-md">
          <h2 className="text-2xl font-bold mb-4">Response:</h2>
          <pre className="whitespace-pre-wrap break-all">{JSON.stringify(responseText, null, 2)}</pre>
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
