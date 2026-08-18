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

INVESTMENT_TOOL_SCHEMA = {
    "name": "investment_agent",
    "description": "Call this when the user asks for investment advice, where to invest, asset allocation, or portfolio suggestions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The exact user question regarding investment"},
            "income": {"type": "number", "description": "Current Income"},
            "expenses": {"type": "number", "description": "Current Expenses"},
            "savings": {"type": "number", "description": "Monthly Savings"},
            "risk": {"type": "string", "description": "Risk Preference"},
            "horizon": {"type": "string", "description": "Investment Horizon"},
            "existing": {"type": "string", "description": "Existing Investments"}
        },
        "required": ["question", "income", "expenses", "savings", "risk", "horizon", "existing"]
    }
}

FORECAST_TOOL_SCHEMA = {
    "name": "forecast_agent",
    "description": "Call this to forecast cash flow, project bank balances for 30, 90, 180, or 365 days.",
    "input_schema": {
        "type": "object",
        "properties": {
            "income": {"type": "number"},
            "expenses": {"type": "number"},
            "current_balance": {"type": "number"}
        },
        "required": ["income", "expenses"]
    }
}

ANOMALY_TOOL_SCHEMA = {
    "name": "anomaly_agent",
    "description": "Call this to detect recurring transactions, subscriptions, and unusual spending anomalies.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

SIMULATION_TOOL_SCHEMA = {
    "name": "simulation_agent",
    "description": "Call this to simulate 'What If' financial scenarios involving varying income, expenses, and goals.",
    "input_schema": {
        "type": "object",
        "properties": {
            "scenario": {"type": "string", "description": "The exact scenario question from the user"}
        },
        "required": ["scenario"]
    }
}

MEMORY_TOOL_SCHEMA = {
    "name": "memory_service",
    "description": "Call this to query user's historical financial memory, past goals, or conversational notes from ChromaDB.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The information to look up"}
        },
        "required": ["query"]
    }
}

INTELLIGENCE_TOOL_SCHEMA = {
    "name": "intelligence_agent",
    "description": "Call this to get comprehensive financial intelligence including mathematical health scores (0-100), overspending risk levels (LOW/HIGH), precise dynamic budget recommendations, and predictive spending insight categorizations.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

from app.ai.llm_client import call_llm_with_tools
import json
import hashlib
from datetime import datetime

_RESPONSE_CACHE = {}

def call_orchestrator(user_id: int, user_message: str, summary_data: Dict[str, Any], transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Cache Check
    cache_key = hashlib.md5(f"{user_id}:{user_message}:{len(transactions)}".encode()).hexdigest()
    if cache_key in _RESPONSE_CACHE:
        return _RESPONSE_CACHE[cache_key]

    messages = [{"role": "user", "content": user_message}]
    
    TOOLS = [EXPENSE_TOOL_SCHEMA, BUDGET_TOOL_SCHEMA, ADVISOR_TOOL_SCHEMA, GOAL_PLANNER_TOOL_SCHEMA, INVESTMENT_TOOL_SCHEMA, FORECAST_TOOL_SCHEMA, ANOMALY_TOOL_SCHEMA, SIMULATION_TOOL_SCHEMA, MEMORY_TOOL_SCHEMA, INTELLIGENCE_TOOL_SCHEMA]
    
    SYSTEM_PROMPT = """You are the central Orchestrator Agent for Finlume AI.
Your job is to read the user's message, understand what they need, and call the appropriate agent/tools to get the data.
You have the following tools:
- expense_agent
- budget_agent
- advisor_agent
- goal_planner_agent
- investment_agent
- forecast_agent
- anomaly_agent
- simulation_agent
- memory_service
- intelligence_agent

If the investment_agent tool is called, you MUST output ONLY the EXACT JSON string returned by the tool as your final reply. Do not add any other conversational text or markdown around it.

If multiple tools are needed, you can call them. But you must answer the user's question directly based on their responses.
"""
    agents_used = []
    
    max_iterations = 5
    for _ in range(max_iterations):
        try:
            response = call_llm_with_tools(
                system_prompt=SYSTEM_PROMPT,
                messages=messages,
                tools=TOOLS,
                max_tokens=1024
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"External AI Call Failed: {e}")
            fallback_explain = {
                "agents_used": ["fallback_system"],
                "confidence_score": 50,
                "reasoning_summary": "System degraded, AI provider unavailable.",
                "key_financial_factors": "Deterministic fallback applied gracefully.",
                "assumptions": "Network or Rate limit exception.",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            fallback_reply = f"My AI analysis capabilities are currently delayed. Your deterministic data (income and expenses) remains available on the dashboard. For reference, income is ₹{summary_data.get('total_income', 0.0):.2f}."
            ret = {"reply": fallback_reply, "agents_used": ["fallback_system"], "explainability": fallback_explain}
            _RESPONSE_CACHE[cache_key] = ret
            return ret
        
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
            
            # Module 1: Explainability
            explainability = {
                "agents_used": agents_used if agents_used else ["general_chat"],
                "confidence_score": 92 if agents_used else 85,
                "reasoning_summary": f"Orchestrated response securely routing through {len(agents_used)} autonomous agents.",
                "key_financial_factors": "Context mapped from holistic transaction timeline.",
                "assumptions": "Assumes historical spending reflects future intent.",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            ret = {"reply": final_text, "agents_used": agents_used, "advisor_data": advisor_data, "explainability": explainability}
            _RESPONSE_CACHE[cache_key] = ret
            return ret
            
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
            elif tool_name == "investment_agent":
                from app.agents.investment_agent import plan_investment
                question = args.get("question", "I need investment advice.")
                income = args.get("income", 0.0)
                expenses = args.get("expenses", 0.0)
                savings = args.get("savings", 0.0)
                risk = args.get("risk", "Medium")
                horizon = args.get("horizon", "Medium Term")
                existing = args.get("existing", "")
                result_str = plan_investment(user_id, question, income, expenses, savings, risk, horizon, existing, summary_data, transactions)
            elif tool_name == "forecast_agent":
                from app.agents.forecast_agent import analyze_forecast
                inc = args.get("income", summary_data.get("total_income", 0.0))
                exp = args.get("expenses", summary_data.get("total_expense", 0.0))
                bal = args.get("current_balance", 0.0)
                result_str = analyze_forecast(inc, exp, bal)
            elif tool_name == "anomaly_agent":
                from app.agents.anomaly_agent import detect_anomalies
                result_str = detect_anomalies(transactions)
            elif tool_name == "simulation_agent":
                from app.agents.simulation_agent import execute_simulation
                scenario = args.get("scenario", "General simulation")
                inc = summary_data.get("total_income", 0.0)
                exp = summary_data.get("total_expense", 0.0)
                result_str = execute_simulation(scenario, inc, exp)
            elif tool_name == "memory_service":
                from app.services.memory_service import memory_service
                q = args.get("query", "Summarize history")
                results = memory_service.query_memory(q)
                result_str = json.dumps([{"id": r.id, "text": r.text, "meta": r.metadata} for r in results])
            elif tool_name == "intelligence_agent":
                from app.services.health_engine import calculate_financial_health
                from app.services.forecast_engine import predict_balances
                from app.services.risk_engine import analyze_risk
                from app.services.insight_engine import generate_insights
                from app.services.recommendation_engine import generate_recommendations
                
                # Fetch profile from DB dynamically or skip explicitly mapping for lightweight chat flow
                # For basic agent use, we will pass None for goals/profile to rely purely on transaction heuristics
                inc = summary_data.get("total_income", 0.0)
                exp = summary_data.get("total_expense", 0.0)
                bal = inc - exp
                
                agg = {
                    "health": calculate_financial_health(transactions, [], None),
                    "forecast": predict_balances(transactions, bal),
                    "risk": analyze_risk(transactions, None),
                    "insights": generate_insights(transactions),
                    "recommendations": generate_recommendations(transactions, None)
                }
                result_str = json.dumps(agg)
            else:
                result_str = f"Error: Unknown tool {tool_name}"
                
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "tool_name": tool_name, # Added for Gemini mapping
                "content": result_str
            })
            
        messages.append({"role": "user", "content": tool_results})
        
    ret = {"reply": "I'm sorry, I needed too many steps to figure this out. Let's try again.", "agents_used": agents_used}
    _RESPONSE_CACHE[cache_key] = ret
    return ret
