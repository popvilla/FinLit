import React from "react";
import { PortfolioInDB, TradeInDB } from "@/lib/models";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PortfolioDashboardProps {
  portfolio: PortfolioInDB;
  trades: TradeInDB[];
}

const PortfolioDashboard: React.FC<PortfolioDashboardProps> = ({ portfolio, trades }) => {
  // For simplicity, let's just show a static chart or a very basic one
  // In a real app, you'd calculate historical portfolio value based on trades and market data
  const chartData = {
    labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
    datasets: [
      {
        label: "Portfolio Value",
        data: [portfolio.balance, portfolio.balance * 1.01, portfolio.balance * 0.99, portfolio.balance * 1.02, portfolio.total_value || portfolio.balance * 1.03],
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Portfolio Value Over Time (Simulated)",
      },
    },
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-700">Current Balance</h3>
          <p className="text-3xl font-bold text-blue-800">${portfolio.balance.toFixed(2)}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg shadow-sm">
          <h3 className="text-lg font-medium text-gray-700">Total Portfolio Value</h3>
          <p className="text-3xl font-bold text-green-800">${(portfolio.total_value || portfolio.balance).toFixed(2)}</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm">
        <Line data={chartData} options={chartOptions} />
      </div>

      <div>
        <h3 className="text-xl font-semibold text-gray-800 mb-3">Recent Trades</h3>
        {trades.length > 0 ? (
          <ul className="space-y-2">
            {trades.map((trade) => (
              <li key={trade.id} className="bg-gray-50 p-3 rounded-md flex justify-between items-center shadow-sm">
                <div>
                  <span className={`font-bold ${trade.side === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>{trade.side}</span> {trade.quantity} shares of {trade.symbol}
                </div>
                <div className="text-gray-600">
                  @{trade.price.toFixed(2)} on {new Date(trade.executed_at).toLocaleDateString()}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-600">No trades yet.</p>
        )}
      </div>
    </div>
  );
};

export default PortfolioDashboard;
