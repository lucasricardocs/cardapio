import streamlit as st
import pandas as pd

# --- DADOS DO CARDÁPIO ---
dados_sanduiches = {
    "Hambúrguer": [
        ("X-Salada Simples", "Pão, hambúrguer, presunto, muçarela, salada, milho e batata", 18),
        ("X-Salada Especial", "Pão, hambúrguer, ovo, presunto, muçarela, salada, milho e batata", 20),
        ("X-Especial Duplo", "Pão, 2 hambúrgueres, ovo, muçarela, presunto, salada, milho e batata", 24),
        ("X-Bacon Simples", "Pão, hambúrguer, bacon, presunto, muçarela, salada, milho e batata", 22),
        ("X-Bacon Especial", "Pão, hambúrguer, bacon, ovo, presunto, muçarela, salada, milho e batata", 24),
        ("X-Bacon Especial Duplo", "Pão, 2 hambúrgueres, bacon, ovo, presunto, muçarela, salada, milho e batata", 27),
        ("X-Tudo", "Pão, hambúrguer, bacon, salsicha, ovo, presunto, muçarela, salada, milho e batata", 27),
        ("X-Hamburgão", "Pão, 2 hambúrgueres, bacon, ovo, 2 salsichas, presunto, muçarela, salada, milho e batata", 35),
        ("X-Mata Fome", "Pão, 2 hambúrgueres, 2 bacons, 2 ovos, 2 salsichas, 2 muçarelas, presunto, salada, milho e batata", 39)
    ],
    "Frango": [
        ("X-Frango Simples", "Pão, filé de frango, presunto, muçarela, salada, milho e batata", 22),
        ("X-Frango Especial", "Pão, filé de frango, ovo, presunto, muçarela, salada, milho e batata", 24),
        ("X-Frango Bacon", "Pão, filé de frango, bacon, presunto, muçarela, salada, milho e batata", 27),
        ("X-Frango Salsicha", "Pão, filé de frango, salsicha, ovo, presunto, muçarela, salada, milho e batata", 27),
        ("X-Frango Tudo", "Pão, filé de frango, bacon, salsicha, ovo, presunto, muçarela, salada, milho e batata", 30),
        ("X-Frango Mata Fome", "Pão, 2 filés de frango, 2 bacons, 2 ovos, 2 salsichas, 2 muçarelas, presunto, salada, milho e batata", 42)
    ],
    "Lombo": [
        ("X-Lombo Simples", "Pão, lombo, presunto, muçarela, salada, milho e batata", 23),
        ("X-Lombo Especial", "Pão, lombo, ovo, presunto, muçarela, salada, milho e batata", 25),
        ("X-Lombo Bacon", "Pão, lombo, bacon, ovo, presunto, muçarela, salada, milho e batata", 28),
        ("X-Lombo Tudo", "Pão, lombo, bacon, salsicha, ovo, presunto, muçarela, salada, milho e batata", 31),
        ("X-Lombo Mata Fome", "Pão, 2 lombos, 2 bacons, 2 ovos, 2 salsichas, 2 muçarelas, presunto, salada, milho e batata", 43)
    ],
    "Filé": [
        ("X-Filé Simples", "Pão, filé bovino, presunto, muçarela, salada, milho e batata", 28),
        ("X-Filé Especial", "Pão, filé bovino, ovo, presunto, muçarela, salada, milho e batata", 30),
        ("X-Filé Bacon", "Pão, filé bovino, bacon, ovo, presunto, muçarela, salada, milho e batata", 33),
        ("X-Filé Tudo", "Pão, filé bovino, bacon, salsicha, ovo, presunto, muçarela, salada, milho e batata", 36),
        ("X-Filé Mata Fome", "Pão, 2 filés bovinos, 2 bacons, 2 ovos, 2 salsichas, 2 muçarelas, presunto, salada, milho e batata", 43)
    ]
}

adicionais = pd.DataFrame({
    "Item": ["Hambúrguer", "Filé de frango", "Filé bovino", "Lombo", "Bacon", "Salsicha", "Ovo", "Muçarela", "Abacaxi", "Molho da Casa", "Cebola"],
    "Preço (R$)": [8, 12, 15, 12, 6, 5, 5, 6, 2, 2, 2]
})

bebidas = pd.DataFrame({
    "Item": [
        "Caldo de Laranja 500ml", "Suco Laranja 500ml", "Suco Caju 500ml", "Suco Maracujá 500ml", "Suco Morango 500ml",
        "Refrigerante lata 350ml", "Refrigerante 600ml", "Refrigerante 1,5L", "Refrigerante 2L", "H2O",
        "Água sem gás", "Água com gás", "Creme Caju 500ml", "Creme Cupuaçu 500ml", "Creme Maracujá 500ml", "Creme Morango 500ml"
    ],
    "Preço (R$)": [12, 10, 10, 12, 10, 7, 10, 12, 15, 8, 3, 4, 15, 15, 15, 15]
})

LOGO_URL = "https://raw.githubusercontent.com/lucasricardocs/clips_dashboard/main/logo.png"

st.set_page_config(
    page_title="Clips Burger - Cardápio",
    layout="centered",
    page_icon=LOGO_URL,
    initial_sidebar_state="collapsed"
)

# --- CSS Customizado (logo à frente do fogo e partículas) ---
st.markdown(f"""
<style>
.logo-fire-container {{
    position: relative;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    margin: 2rem auto 1.5rem auto;
    height: 230px;
    width: 100%;
    max-width: 400px;
    z-index: 1;
}}
.fire-logo {{
    position: absolute;
    left: 50%;
    bottom: 30px;
    transform: translateX(-50%);
    z-index: 100;
    max-width: 170px;
    width: auto;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 0 20px rgba(255,69,0,0.8));
    animation: logoFloat 3s ease-in-out infinite;
}}
@keyframes logoFloat {{
    0%,100% {{ transform: translateX(-50%) translateY(0px) scale(1);}}
    50% {{ transform: translateX(-50%) translateY(-10px) scale(1.05);}}
}}
.fire-container {{
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 100px;
    z-index: 10;
    pointer-events: none;
}}
.flame {{ position: absolute; bottom: 0; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%; transform-origin: center bottom; animation: flicker 0.5s ease-in-out infinite alternate; z-index: 11;}}
@keyframes flicker {{
    0% {{ opacity: 0.8; }}
    50% {{ opacity: 1; }}
    100% {{ opacity: 0.9; }}
}}
.flame-red {{
    left: 50%; transform: translateX(-50%);
    width: 60px; height: 90px;
    background: radial-gradient(circle, #ff4500 0%, #ff6347 30%, #dc143c 70%, #8b0000 100%);
    box-shadow: 0 0 30px #ff4500, 0 0 60px #ff6347;
    animation-duration: 0.8s;
}}
.flame-orange {{
    left: 43%; transform: translateX(-50%);
    width: 40px; height: 60px;
    background: radial-gradient(circle, #ffa500 0%, #ff8c00 50%, #ff4500 100%);
    box-shadow: 0 0 25px #ffa500, 0 0 50px #ff8c00;
    animation-duration: 0.6s; animation-delay: 0.2s;
}}
.flame-yellow {{
    left: 57%; transform: translateX(-50%);
    width: 25px; height: 40px;
    background: radial-gradient(circle, #ffff00 0%, #ffd700 50%, #ffa500 100%);
    box-shadow: 0 0 20px #ffff00, 0 0 40px #ffd700;
    animation-duration: 0.4s; animation-delay: 0.4s;
}}
.flame-white {{
    left: 50%; transform: translateX(-50%);
    width: 15px; height: 25px;
    background: radial-gradient(circle, #ffffff 0%, #ffff99 50%, #ffd700 100%);
    box-shadow: 0 0 15px #ffffff, 0 0 30px #ffff99;
    animation-duration: 0.3s; animation-delay: 0.1s;
}}
/* Partículas de fogo (fagulhas) - atrás da logo */
.fire-particle {{
    position: absolute;
    bottom: 0;
    border-radius: 50%;
    animation: particle-rise-high linear infinite;
    pointer-events: none;
    z-index: 5;
    opacity: 1;
}}
@keyframes particle-rise-high {{
    0% {{ bottom: 0px; opacity: 1; transform: translateX(0) scale(1);}}
    100% {{ bottom: 120px; opacity: 0; transform: translateX(var(--random-x, 0px)) scale(0.4);}}
}}
.fire-particle.small {{ width: 4px; height: 4px; background: #ffed8b;}}
.fire-particle.medium {{ width: 7px; height: 7px; background: #ffa500;}}
.fire-particle.large {{ width: 10px; height: 10px; background: #ff9800;}}
.menu-container {{
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 1.2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border: 1px solid #475569;
    margin: 2.2rem auto 2.2rem auto;
    padding: 1.5rem 1.2rem 1.2rem 1.2rem;
    max-width: 480px;
}}
.menu-title {{
    color: #fbbf24;
    font-size: 1.4rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1.2rem;
    letter-spacing: 1px;
    text-shadow: 0 2px 8px #000b;
}}
.menu-item {{
    background: linear-gradient(135deg, #334155 0%, #475569 100%);
    border-radius: 1rem;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.10);
    border: 1px solid #475569;
    display: flex;
    flex-direction: column;
    gap: 0.2em;
}}
.item-title {{ font-weight: 600; font-size: 1.1rem; color: #f8fafc; margin-bottom: 0.2em;}}
.item-desc {{ color: #cbd5e1; font-size: 0.97rem; margin-bottom: 0.2em;}}
.item-price {{ color: #22c55e; font-weight: bold; font-size: 1.1rem; align-self: flex-end;}}
.menu-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #334155 0%, #475569 100%);
    border-radius: 0.7rem;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
.menu-table th, .menu-table td {{
    padding: 0.7em 0.5em;
    text-align: left;
    font-size: 1rem;
}}
.menu-table th {{
    background: #374151;
    color: #f8fafc;
    font-weight: 600;
    border-bottom: 1px solid #475569;
}}
.menu-table td {{
    color: #e2e8f0;
    border-bottom: 1px solid #475569;
}}
.menu-table tr:last-child td {{ border-bottom: none; }}
</style>
""", unsafe_allow_html=True)

# --- LOGO ANIMADA COM FOGO E FAGULHAS (logo sempre à frente) ---
st.markdown(f"""
<div class="logo-fire-container">
    <div class="fire-container">
        <div class="flame flame-red"></div>
        <div class="flame flame-orange"></div>
        <div class="flame flame-yellow"></div>
        <div class="flame flame-white"></div>
        <div class="fire-particle small" style="left: 5%; animation-delay: 0s; animation-duration: 3.4s; --random-x: -12px;"></div>
        <div class="fire-particle medium" style="left: 20%; animation-delay: 0.5s; animation-duration: 3.8s; --random-x: 20px;"></div>
        <div class="fire-particle large" style="left: 40%; animation-delay: 1.1s; animation-duration: 4.2s; --random-x: -18px;"></div>
        <div class="fire-particle small" style="left: 60%; animation-delay: 0.7s; animation-duration: 3.6s; --random-x: 15px;"></div>
        <div class="fire-particle medium" style="left: 80%; animation-delay: 1.4s; animation-duration: 4.0s; --random-x: -22px;"></div>
    </div>
    <img src="{LOGO_URL}" class="fire-logo" alt="Clips Burger Logo">
</div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; margin-bottom:2rem;'>Cardápio</h1>", unsafe_allow_html=True)

# --- CARDÁPIO POR CATEGORIA ---
for categoria, itens in dados_sanduiches.items():
    st.markdown(f'<div class="menu-container"><div class="menu-title">{categoria}</div>', unsafe_allow_html=True)
    for nome, desc, preco in itens:
        st.markdown(
            f'<div class="menu-item">'
            f'<span class="item-title">{nome}</span>'
            f'<span class="item-desc">{desc}</span>'
            f'<span class="item-price">R$ {preco:.2f}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --- ADICIONAIS ---
st.markdown('<div class="menu-container"><div class="menu-title">➕ Adicionais</div>', unsafe_allow_html=True)
st.markdown(adicionais.to_html(classes="menu-table", index=False), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- BEBIDAS ---
st.markdown('<div class="menu-container"><div class="menu-title">🥤 Bebidas</div>', unsafe_allow_html=True)
st.markdown(bebidas.to_html(classes="menu-table", index=False), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
