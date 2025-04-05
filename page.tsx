// ...
import React from "react";
import { useCoAgentStateRender } from "@copilotkit/react-core";
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
 

  // styles omitted for brevity
  useCoAgentStateRender<AgentState>({
    name: "sample_agent", // the name the agent is served as
    render: ({ state }) => (
      <div>
        {state.searches?.map((search, index) => (
          <div key={index}>
            {search.done ? "✅" : "❌"} {search.query}{search.done ? "" : "..."}
          </div>
        ))}
      </div>
    ),
  });
 
  // ...
 
  return <div>...</div>;
}