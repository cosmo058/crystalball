import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import StockDetail from "./pages/StockDetail";
import Watchlist from "./pages/Watchlist";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-surface text-slate-200">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/stock/:ticker" element={<StockDetail />} />
            <Route path="/watchlist" element={<Watchlist />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
