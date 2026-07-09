import os
from typing import Dict, Any, List
from app.core.config import settings
from app.agents.expense_agent import analyze_expenses
from app.agents.budget_agent import plan_budget

# Define tool schemas for Claude
EXPENSE_TOOL_SCHEMA = {
    "name": "expense_agent",
    "description": "Analyzes a user's transaction list and returns a summary of expenses and top spending categories. Use this when the user asks about their spending, expenses, or transactions.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

BUDGET_TOOL_SCHEMA = {
    "name": "budget_agent",
    "description": "Creates a budget plan based on the user's total income, total expenses, and top categories. Use this when the user asks for budgeting advice, saving targets, or how to manage their money.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

from app.ai.llm_client import call_llm_with_tools

def call_orchestrator(user_message: str, summary_data: Dict[str, Any], transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    messages = [{"role": "user", "content": user_message}]
    
    system_prompt = (
        "You are Finlume AI, a friendly, professional financial coach.\n"
        "You have access to tools that can analyze expenses and plan budgets based on the user's data.\n"
        "Use these tools if the user's request requires it, or answer directly if you don't need them.\n"
        "Provide concise, encouraging, and highly actionable advice (1-3 paragraphs max)."
    )

    tools = [EXPENSE_TOOL_SCHEMA, BUDGET_TOOL_SCHEMA]
    agents_used = []
    
    max_iterations = 5
    for _ in range(max_iterations):
        response = call_llm_with_tools(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
            max_tokens=1024
        )
        
        # Append LLM's response to the conversation
        messages.append({"role": "assistant", "content": response.content})
        
        # Check if LLM decided to use a tool
        tool_uses = [c for c in response.content if c.type == "tool_use"]
        
        if not tool_uses:
            # No tool use requested, LLM provided a final text response.
            final_text = "".join(c.text for c in response.content if c.type == "text")
            return {"reply": final_text, "agents_used": agents_used}
            
        # Execute each tool requested
        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_id = tool_use.id
            
            if tool_name not in agents_used:
                agents_used.append(tool_name)
                
            if tool_name == "expense_agent":
                result_str = analyze_expenses(transactions)
            elif tool_name == "budget_agent":
                top_cats_dicts = [{"category": c[0], "amount": c[1]} for c in summary_data.get("top_categories", [])]
                result_str = plan_budget(summary_data.get("total_income", 0.0), summary_data.get("total_expense", 0.0), top_cats_dicts)
            else:
                result_str = f"Error: Unknown tool {tool_name}"
                
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "tool_name": tool_name, # Added for Gemini mapping
                "content": result_str
            })
            
        messages.append({"role": "user", "content": tool_results})
        
    return {"reply": "I'm sorry, I needed too many steps to figure this out. Let's try again.", "agents_used": agents_used}
