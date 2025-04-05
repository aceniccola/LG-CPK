import React from "react";
import { useCoAgent } from "@copilotkit/react-core"; 
import { useStreamingContent } from "@/lib/hooks/useStreamingContent";
// ...
 
// Define the state of the agent, should match the state of the agent in your LangGraph.
type AgentState = {
  searches: {
    query: string;
    done: boolean;
  }[];
};
 
function YourMainContent() {
  // ... 
 

  const { state } = useCoAgent<AgentState>({
    name: "sample_agent", // the name the agent is served as
  })
 
  // ...
 
  return (
    <div>
      {/* ... */}
      <div className="flex flex-col gap-2 mt-4">

        {state.searches?.map((search, index) => (
          <div key={index} className="flex flex-row">
            {search.done ? "✅" : "❌"} {search.query}
          </div>
        ))}
      </div>
    </div>
  )
}