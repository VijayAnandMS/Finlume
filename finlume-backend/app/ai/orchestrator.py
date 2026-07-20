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

from app.agents.advisor_agent import analyze_financial_decision

ADVISOR_TOOL_SCHEMA = {
    "name": "advisor_agent",
    "description": "Calculates financial affordability, risk levels, and provides specific recommendations based on user cash flow. Use this when the user asks for financial advice on purchasing, affordability, or risk.",
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The financial question to analyze"},
            "context": {"type": "object", "description": "Any additional context"},
            "user_id": {"type": "integer", "description": "The user's ID"}
        },
        "required": ["question"]
    }
}

GOAL_PLANNER_TOOL_SCHEMA = {
    "name": "goal_planner_agent",
    "description": "Creates actionable saving strategies and orchestrates financial planning for a specific user goal.",
    "input_schema": {
        "type": "object",
        "properties": {
            "goal_name": {"type": "string", "description": "The name of the goal"},
            "target_amount": {"type": "number", "description": "Target amount to save"},
            "deadline": {"type": "string", "description": "The target date or duration"}
        },
        "required": ["goal_name", "target_amount"]
    }
}

from app.ai.llm_client import call_llm_with_tools
import json

def call_orchestrator(user_id: int, user_message: str, summary_data: Dict[str, Any], transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    messages = [{"role": "user", "content": user_message}]
    
    system_prompt = (
        "You are Finlume AI, a friendly, professional financial coach.\n"
        "You have access to tools that can analyze expenses, plan budgets, and act as a financial advisor based on the user's data.\n"
        "Use these tools if the user's request requires it, or answer directly if you don't need them.\n"
        "The planner should NOT call the advisor for unrelated questions.\n"
        f"For reference, the current user_id is {user_id}.\n"
        "Provide concise, encouraging, and highly actionable advice (1-3 paragraphs max)."
    )

    tools = [EXPENSE_TOOL_SCHEMA, BUDGET_TOOL_SCHEMA, ADVISOR_TOOL_SCHEMA, GOAL_PLANNER_TOOL_SCHEMA]
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
            
            # Extract advisor_data if it exists in the tool results history
            advisor_data = None
            for m in messages:
                if m["role"] == "user" and isinstance(m["content"], list):
                    for b in m["content"]:
                        if isinstance(b, dict) and b.get("tool_name") == "advisor_agent":
                            try:
                                advisor_data = json.loads(b["content"])
                            except:
                                pass
            
            return {"reply": final_text, "agents_used": agents_used, "advisor_data": advisor_data}
            
        # Execute each tool requested
        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_id = tool_use.id
            args = getattr(tool_use, "input", {})
            
            if tool_name not in agents_used:
                agents_used.append(tool_name)
                
            if tool_name == "expense_agent":
                result_str = analyze_expenses(transactions)
            elif tool_name == "budget_agent":
                top_cats_dicts = [{"category": c[0], "amount": c[1]} for c in summary_data.get("top_categories", [])]
                result_str = plan_budget(summary_data.get("total_income", 0.0), summary_data.get("total_expense", 0.0), top_cats_dicts)
            elif tool_name == "advisor_agent":
                question = args.get("question", user_message)
                # Inject total_income and total_expense into context
                context = args.get("context", {})
                context["total_income"] = summary_data.get("total_income", 0.0)
                context["total_expense"] = summary_data.get("total_expense", 0.0)
                
                advisor_result = analyze_financial_decision(
                    user_id=args.get("user_id", user_id),
                    question=question,
                    context=context
                )
                result_str = json.dumps(advisor_result)
            elif tool_name == "goal_planner_agent":
                from app.agents.goal_planner_agent import plan_goal
                goal_name = args.get("goal_name", "Unnamed Goal")
                target = args.get("target_amount", 0.0)
                deadline = args.get("deadline", "TBD")
                result_str = plan_goal(user_id, goal_name, target, deadline, summary_data, transactions)
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
