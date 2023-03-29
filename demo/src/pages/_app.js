import '@/styles/globals.css';
import Navbar from '../components/Navbar';

function App({ Component, pageProps }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <Component {...pageProps} />
    </div>
  );
}

export default App;