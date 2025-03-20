import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Modelo de dados para entrada dos gráficos
class ChartData(BaseModel):
    pizza_chart: Dict[str, float]
    bar_chart: Dict[str, float]
    pizza_title: str = "Pizza Chart"
    bar_title: str = "Bar Chart"
    pizza_color_palette: List[str] = Field(default_factory=lambda: [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', 
        '#FF9F40', '#FF6384', '#C9CBCF'
    ])
    bar_color_palette: List[str] = Field(default_factory=lambda: [
        '#003f5c', '#2f4b7c', '#665191', '#a05195', 
        '#d45087', '#ff6e54', '#ffa600'
    ])

# Modelo de resposta com a imagem em base64
class ChartResponse(BaseModel):
    image: str

# Inicialização do FastAPI
app = FastAPI(title="COFIPEI - Gerador de Gráficos Financeiros")

def generate_chart(chart_data: ChartData) -> str:
    # Configurar o gráfico
    plt.figure(figsize=(16, 8))
    
    # Configurar subplots
    gs = plt.GridSpec(1, 2, width_ratios=[1, 1])
    
    # Gráfico de Pizza (subplot esquerdo)
    ax1 = plt.subplot(gs[0])
    pizza_labels = list(chart_data.pizza_chart.keys())
    pizza_values = list(chart_data.pizza_chart.values())
    
    ax1.pie(
        pizza_values, 
        labels=pizza_labels, 
        colors=chart_data.pizza_color_palette[:len(pizza_labels)],
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85
    )
    ax1.set_title(chart_data.pizza_title)
    
    # Gráfico de Barras (subplot direito)
    ax2 = plt.subplot(gs[1])
    bar_labels = list(chart_data.bar_chart.keys())
    bar_values = list(chart_data.bar_chart.values())
    
    bars = ax2.bar(
        bar_labels, 
        bar_values, 
        color=chart_data.bar_color_palette[:len(bar_labels)]
    )
    ax2.set_title(chart_data.bar_title)
    ax2.set_xlabel('Categorias')
    ax2.set_ylabel('Valores')
    
    # Rotacionar labels do eixo x para evitar sobreposição
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Adicionar valores no topo de cada barra
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width()/2., 
            height,
            f'{height:.2f}',
            ha='center', 
            va='bottom'
        )
    
    # Ajustar layout
    plt.tight_layout()
    
    # Salvar gráfico em um buffer de memória
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    
    # Converter para base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

# Endpoint para geração de gráficos
@app.post("/generate-chart", response_model=ChartResponse)
def create_chart(chart_data: ChartData):
    image = generate_chart(chart_data)
    return {"image": image}

# Exemplo de uso na documentação
"""
Exemplo de Requisição:
POST /generate-chart
{
    "pizza_chart": {
        "Alimentação": 500.00,
        "Transporte": 300.00,
        "Lazer": 200.00,
        "Outros": 100.00
    },
    "bar_chart": {
        "Jan": 1000.00,
        "Fev": 1200.00,
        "Mar": 1500.00,
        "Abr": 1300.00
    },
    "pizza_title": "Despesas por Categoria",
    "bar_title": "Receitas Mensais"
}
"""

# Para rodar a aplicação:
# uvicorn main:app --reload
