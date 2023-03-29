import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-5">
      <h1 className="text-4xl font-bold mb-5">Welcome</h1>
      <div className="space-y-4">
        <Link href="/upload" legacyBehavior>
          <a className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10">
            Copilot Upload
          </a>
        </Link>
        <Link href="/query" legacyBehavior>
          <a className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10">
            Copilot Query
          </a>
        </Link>
      </div>
    </div>
  );
}