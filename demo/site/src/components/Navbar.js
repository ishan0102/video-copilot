import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-indigo-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link href="/" legacyBehavior>
                  <a className="text-white px-3 py-2 rounded-md text-sm font-medium">
                    Home
                  </a>
                </Link>
                <Link href="/upload" legacyBehavior>
                  <a className="text-white px-3 py-2 rounded-md text-sm font-medium">
                    Copilot Upload
                  </a>
                </Link>
                <Link href="/query" legacyBehavior>
                  <a className="text-white px-3 py-2 rounded-md text-sm font-medium">
                    Copilot Query
                  </a>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
