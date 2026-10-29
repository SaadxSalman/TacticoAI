export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-white p-8">
      <h1 className="text-4xl font-bold mb-6">
        🏀 TacticoAI Dashboard
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Injury Risk Card -->
        <div className="bg-white rounded-lg shadow-sm dark:bg-gray-800 p-6">
          <h3 className="text-xl font-medium mb-4">Injury Risk Assessment</h3>
          <p className="text-gray-600">View player fatigue and risk levels</p>
        </div>
        
        <!-- Tactical Analysis Card -->
        <div className="bg-white rounded-lg shadow-sm dark:bg-gray-800 p-6">
          <h3 className="text-xl font-medium mb-4">Tactical Analysis</h3>
          <p className="text-gray-600">Explore formation counters and strategies</p>
        </div>
        
        <!-- Performance Metrics Card -->
        <div className="bg-white rounded-lg shadow-sm dark:bg-gray-800 p-6">
          <h3 className="text-xl font-medium mb-4">Performance Metrics</h3>
          <p className="text-gray-600">Player stats and trends</p>
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Natural Language Query</h2>
        <p className="text-gray-600">
          Ask questions about player performance, tactics, and strategies
        </h2>
      </div>
    </div>
  )
}