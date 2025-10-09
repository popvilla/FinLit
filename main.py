<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from typing import List
from datetime import datetime

from .database import supabase
from .models import (
    UserCreate, UserInDB, Token, PortfolioBase, PortfolioInDB, 
    TradeBase, TradeInDB, MarketEventInDB, ChatbotInteractionBase, 
    ChatbotInteractionInDB, WebinarBase, WebinarInDB
)
from .auth import get_password_hash, verify_password, create_access_token, get_current_user, get_current_active_user, get_current_admin_user, get_current_instructor_user, get_current_student_user
from .market_simulator import simulate_trade_execution, calculate_portfolio_value # Placeholder
from .chatbot import get_chatbot_response # Placeholder

app = FastAPI(
    title="FinLit API",
    description="Backend API for the FinLit financial literacy application.",
    version="0.1.0",
)

# CORS Middleware for frontend communication
origins = [
    "http://localhost:3000", # Frontend URL
    # Add other production origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to FinLit API!"}

# --- Authentication Endpoints ---

@app.post("/signup", response_model=UserInDB, tags=["Auth"])
async def signup_user(user_data: UserCreate):
    # Check if user already exists
    response = supabase.table("users").select("id").eq("email", user_data.email).execute()
    if response.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = hashed_password
    del user_dict["password"]

    response = supabase.table("users").insert(user_dict).execute()
    if response.data:
        new_user = UserInDB(**response.data[0])
        # Create a default portfolio for new students
        if new_user.role == 'student':
            portfolio_data = PortfolioBase(user_id=new_user.id)
            supabase.table("portfolios").insert(portfolio_data.model_dump()).execute()
        return new_user
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registration failed")

@app.post("/token", response_model=Token, tags=["Auth"])
async def login_for_access_token(form_data: UserCreate):
    response = supabase.table("users").select("id, email, password_hash, role").eq("email", form_data.email).single().execute()
    user_data = response.data

    if not user_data or not verify_password(form_data.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user_data["id"]), "role": user_data["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserInDB, tags=["Auth"])
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user

# --- Portfolio Endpoints ---

@app.get("/portfolios/{user_id}", response_model=PortfolioInDB, tags=["Portfolio"])
async def get_portfolio(user_id: UUID, current_user: UserInDB = Depends(get_current_student_user)):
    if current_user.id != user_id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this portfolio")
    
    response = supabase.table("portfolios").select("*").eq("user_id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return PortfolioInDB(**response.data)

# --- Trade Endpoints ---

@app.post("/trades", response_model=TradeInDB, tags=["Trade"])
async def execute_trade(trade_data: TradeBase, current_user: UserInDB = Depends(get_current_student_user)):
    # Verify portfolio ownership
    portfolio_response = supabase.table("portfolios").select("user_id, balance").eq("id", trade_data.portfolio_id).single().execute()
    if not portfolio_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    
    if portfolio_response.data["user_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to trade for this portfolio")
    
    portfolio_balance = portfolio_response.data["balance"]
    trade_cost = trade_data.quantity * trade_data.price

    if trade_data.side == 'BUY':
        if portfolio_balance < trade_cost:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance for this trade")
        new_balance = portfolio_balance - trade_cost
    elif trade_data.side == 'SELL':
        # In a real app, you'd check if the user holds enough of the stock
        # For simplicity, we'll allow selling without checking holdings for now.
        new_balance = portfolio_balance + trade_cost
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trade side")
    
    # Simulate trade execution and update portfolio (simplified)
    # In a real system, this would involve more complex market simulation and holdings update.
    updated_portfolio = supabase.table("portfolios").update({"balance": new_balance}).eq("id", trade_data.portfolio_id).execute()
    
    trade_dict = trade_data.model_dump()
    response = supabase.table("trades").insert(trade_dict).execute()
    if response.data:
        return TradeInDB(**response.data[0])
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Trade execution failed")

@app.get("/portfolios/{portfolio_id}/trades", response_model=List[TradeInDB], tags=["Trade"])
async def get_portfolio_trades(portfolio_id: UUID, current_user: UserInDB = Depends(get_current_student_user)):
    # Verify portfolio ownership
    portfolio_response = supabase.table("portfolios").select("user_id").eq("id", portfolio_id).single().execute()
    if not portfolio_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    
    if portfolio_response.data["user_id"] != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these trades")
    
    response = supabase.table("trades").select("*").eq("portfolio_id", portfolio_id).order("executed_at", desc=True).limit(50).execute()
    return [TradeInDB(**trade) for trade in response.data]

# --- Market Simulation Endpoints ---

@app.get("/market-events", response_model=List[MarketEventInDB], tags=["Market Simulation"])
async def get_market_events(current_user: UserInDB = Depends(get_current_active_user)):
    # This endpoint is accessible to any logged-in user
    response = supabase.table("market_events").select("*").order("event_date", desc=True).limit(20).execute()
    return [MarketEventInDB(**event) for event in response.data]

# --- Chatbot Endpoints ---

@app.post("/chatbot/ask", response_model=ChatbotInteractionInDB, tags=["Chatbot"])
async def ask_chatbot(query: str, current_user: UserInDB = Depends(get_current_active_user)):
    # Integrate with OpenAI API here
    response_text = get_chatbot_response(query, current_user.id) # Placeholder function
    
    interaction_data = ChatbotInteractionBase(
        user_id=current_user.id,
        query=query,
        response=response_text
    )
    response = supabase.table("chatbot_interactions").insert(interaction_data.model_dump()).execute()
    if response.data:
        return ChatbotInteractionInDB(**response.data[0])
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chatbot interaction failed")

@app.get("/chatbot/history", response_model=List[ChatbotInteractionInDB], tags=["Chatbot"])
async def get_chatbot_history(current_user: UserInDB = Depends(get_current_active_user)):
    response = supabase.table("chatbot_interactions").select("*").eq("user_id", current_user.id).order("interaction_at", desc=True).limit(50).execute()
    return [ChatbotInteractionInDB(**interaction) for interaction in response.data]

# --- Webinar Endpoints ---

@app.get("/webinars", response_model=List[WebinarInDB], tags=["Webinars"])
async def get_webinars(current_user: UserInDB = Depends(get_current_active_user)):
    response = supabase.table("webinars").select("*").order("scheduled_at", desc=True).execute()
    return [WebinarInDB(**webinar) for webinar in response.data]

@app.post("/webinars", response_model=WebinarInDB, tags=["Webinars"])
async def create_webinar(webinar_data: WebinarBase, current_user: UserInDB = Depends(get_current_instructor_user)):
    # Ensure the instructor_id matches the current authenticated instructor
    if webinar_data.instructor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create webinar for another instructor")

    response = supabase.table("webinars").insert(webinar_data.model_dump()).execute()
    if response.data:
        return WebinarInDB(**response.data[0])
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webinar creation failed")
=======
def main():
    print("Hello from golden-child!")


if __name__ == "__main__":
    main()
>>>>>>> origin/Genesis
