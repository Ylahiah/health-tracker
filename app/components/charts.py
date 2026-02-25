import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_weight_history(df):
    """
    Plots weight history over time.
    """
    if df.empty:
        return None
    
    fig = px.line(df, x="date", y="weight", title="Progreso de Peso", markers=True)
    fig.update_layout(xaxis_title="Fecha", yaxis_title="Peso (kg)")
    return fig

def plot_calories_vs_goal(df, calorie_goal):
    """
    Plots daily calorie intake vs goal.
    """
    if df.empty:
        return None
        
    # Group by date if multiple entries per day
    daily = df.groupby("date")["calories"].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["date"], y=daily["calories"], name="Consumo"))
    fig.add_trace(go.Scatter(x=daily["date"], y=[calorie_goal]*len(daily), mode="lines", name="Meta"))
    
    fig.update_layout(title="Calorías Diarias vs Meta", xaxis_title="Fecha", yaxis_title="Calorías")
    return fig

def plot_macronutrients(protein, carbs, fats):
    """
    Plots a pie chart of macronutrient distribution.
    """
    labels = ['Proteína', 'Carbohidratos', 'Grasas']
    values = [protein, carbs, fats]
    
    if sum(values) == 0:
        return None

    fig = px.pie(values=values, names=labels, title="Distribución de Macros")
    return fig
