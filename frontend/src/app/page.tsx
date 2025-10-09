"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import AuthForm from "@/components/AuthForm";
import PortfolioDashboard from "@/components/PortfolioDashboard";
import TradeForm from "@/components/TradeForm";
import ChatbotWidget from "@/components/ChatbotWidget";
import { PortfolioInDB, TradeInDB, UserInDB, ChatbotInteractionInDB } from "@/lib/models";
import { getPortfolio, getPortfolioTrades, getChatbotHistory } from "@/lib/api";

export default function Home() {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();
  const [portfolio, setPortfolio] = useState<PortfolioInDB | null>(null);
  const [trades, setTrades] = useState<TradeInDB[]>([]);
  const [chatbotHistory, setChatbotHistory] = useState<ChatbotInteractionInDB[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/"); // Redirect to home/auth if not logged in
    }
    if (user) {
      fetchUserData(user);
    }
  }, [user, loading, router]);

  const fetchUserData = async (currentUser: UserInDB) => {
    try {
      const userPortfolio = await getPortfolio(currentUser.id);
      setPortfolio(userPortfolio);
      if (userPortfolio) {
        const userTrades = await getPortfolioTrades(userPortfolio.id);
        setTrades(userTrades);
        const history = await getChatbotHistory();
        setChatbotHistory(history);
      }
    } catch (err: any) {
      console.error("Error fetching user data:", err);
      setError(err.message || "Failed to fetch user data.");
    }
  };

  const handleTradeExecuted = async () => {
    if (user && portfolio) {
      await fetchUserData(user);
    } else if (user) {
       // If portfolio was null, try fetching again in case it was just created
       await fetchUserData(user);
    }
  };

  const handleChatbotInteraction = async () => {
    if (user) {
      const history = await getChatbotHistory();
      setChatbotHistory(history);
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-screen text-xl">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <AuthForm />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <header className="flex justify-between items-center py-4 px-6 bg-white shadow-md rounded-lg mb-6">
        <h1 className="text-3xl font-bold text-gray-800">FinLit Dashboard</h1>
        <div className="flex items-center space-x-4">
          <span className="text-lg text-gray-700">Welcome, {user.email} ({user.role})</span>
          <button
            onClick={signOut}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </header>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">My Portfolio</h2>
            {portfolio ? (
              <PortfolioDashboard portfolio={portfolio} trades={trades} />
            ) : (
              <p className="text-gray-600">Loading portfolio...</p>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Execute Trade</h2>
            {portfolio ? (
              <TradeForm portfolioId={portfolio.id} onTradeExecuted={handleTradeExecuted} />
            ) : (
              <p className="text-gray-600">Please wait for portfolio to load to trade.</p>
            )}
          </div>
        </div>

        <div className="md:col-span-1 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">FinLit Chatbot</h2>
          <ChatbotWidget userId={user.id} history={chatbotHistory} onNewInteraction={handleChatbotInteraction} />
        </div>
      </div>
    </div>
  );
}
