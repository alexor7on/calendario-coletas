import re
import io
import calendar
import unicodedata
import base64
from datetime import datetime, date

from streamlit_searchbox import st_searchbox
import pandas as pd
import streamlit as st
import traceback
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Calendário de Coletas",
    page_icon="📅",
    layout="wide"
)

# =========================
# ESTILO DA TELA DE LOGIN
# =========================
def aplicar_estilo_login():
    st.markdown("""
    <style>
        header {visibility: hidden;}
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }

        .stApp {
            background: linear-gradient(135deg, #f5f9ff 0%, #eef4ff 100%);
        }

        .login-card {
            background: white;
            padding: 26px 22px 20px 22px;
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(16, 24, 40, 0.10);
            border: 1px solid rgba(0,0,0,0.05);
            max-width: 420px;
            margin: 0 auto;
        }

        .login-top-bar {
            height: 6px;
            width: 100%;
            background: linear-gradient(90deg, #0A5CFF 0%, #3B82F6 100%);
            border-radius: 999px;
            margin-bottom: 18px;
        }

        .login-title {
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 6px;
            text-align: center;
        }

        .login-subtitle {
            font-size: 14px;
            color: #475569;
            margin-bottom: 18px;
            text-align: center;
            line-height: 1.4;
        }

        .login-footer {
            margin-top: 12px;
            text-align: center;
            font-size: 11px;
            color: #94a3b8;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 10px !important;
            border: 1px solid #cbd5e1 !important;
            padding: 0.75rem 0.9rem !important;
            font-size: 14px !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border: 1px solid #0A5CFF !important;
            box-shadow: 0 0 0 3px rgba(10, 92, 255, 0.15) !important;
        }

        div.stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #0A5CFF 0%, #3B82F6 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 0.9rem;
            font-size: 14px;
            font-weight: 700;
        }

        div[data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)


# =========================
# FUNÇÃO DE LOGIN
# =========================
def tela_login():
    aplicar_estilo_login()

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    senha_correta = st.secrets.get("APP_PASSWORD", "")

    if st.session_state["autenticado"]:
        return True

    # Espaço vertical para descer/subir a caixa
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)

    # Centraliza horizontalmente
    col_esq, col_centro, col_dir = st.columns([1.2, 1, 1.2])

    with col_centro:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-top-bar"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-title">Portal de Coletas</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="login-subtitle">Acesse o calendário de coletas informando a senha de acesso.</div>',
            unsafe_allow_html=True
        )

        with st.form("form_login", clear_on_submit=False):
            senha_digitada = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha"
            )
            entrar = st.form_submit_button("Acessar")

            if entrar:
                if senha_digitada == senha_correta:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta. Tente novamente.")

        st.markdown(
            '<div class="login-footer">Acesso restrito</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

    # =========================
    # FORMULÁRIO
    # =========================
    with st.form("form_login", clear_on_submit=False):
        senha_digitada = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha"
        )

        entrar = st.form_submit_button("Acessar")

        if entrar:
            if senha_digitada == senha_correta:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")

    st.markdown(
        '<div class="login-footer">Acesso restrito</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Impede o restante do app de rodar
    st.stop()

tela_login()

# BOTÃO DE LOGOUT
if st.session_state.get("autenticado"):
    with st.sidebar:
        st.markdown("### 🔐 Acesso")
        if st.button("Sair"):
            st.session_state["autenticado"] = False
            st.rerun()

# =========================
# CHAMA O LOGIN ANTES DO APP
# =========================
tela_login()


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


logo_base64 = get_base64_image("logo.png")


# =========================================================
# CONFIGURAÇÕES DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Calendário de Coletas",
    page_icon="📦",
    layout="wide"
)

# =========================================================
# CSS / ESTILO
# =========================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    .hero {
        background: linear-gradient(135deg, #1A73E8 0%, #0B3C91 100%);
        padding: 28px 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(26, 115, 232, 0.18);
    }

    .hero-inner {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .hero-logo {
        height: 44px;
        object-fit: contain;
        display: block;
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .hero p {
        margin: 6px 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 18px;
        padding: 18px 18px 10px 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 4px;
    }

    .section-subtitle {
        font-size: 0.92rem;
        color: #6B7280;
        margin-bottom: 16px;
    }

    .info-chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: #EEF4FF;
        color: #1A73E8;
        font-size: 0.84rem;
        font-weight: 600;
        margin-top: 6px;
    }

    .result-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 4px;
    }

    .footer-note {
        text-align: center;
        color: #6B7280;
        font-size: 0.84rem;
        padding-top: 8px;
    }

    div[data-testid="stRadio"] > div {
        gap: 12px;
    }

    div[data-testid="stCodeBlock"] {
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero" style="display: flex; align-items: center; justify-content: space-between;">

<div style="display: flex; align-items: center; height: 100%;">
<h1 style="margin: 0;">Calendário de Coletas Nuvem Envio</h1>
</div>

<img src="data:image/png;base64,{logo_base64}" 
     style="height: 125px; opacity: 0.95; margin-right: 20px;" />

</div>
""", unsafe_allow_html=True)


# =========================================================
# CONFIGURAÇÕES INICIAIS
# =========================================================
ID_ARQUIVO_DRIVE = "1Kzyi1kv0Jq7SahKFfy_jUohKTm1XphGA"

MESES_PT = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

MESES_PT_REV = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def normalizar_texto(texto: str) -> str:
    if texto is None:
        return ""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto


def estado_da_aba(nome_aba: str):
    nome = normalizar_texto(nome_aba)

    if re.search(r"\bmg\b", nome) or "minas" in nome:
        return "MG"

    if re.search(r"\bsp\b", nome) or re.search(r"\bspi\b", nome):
        return "SP"

    return None


def extrair_mes_ano_da_aba(nome_aba: str):
    nome = normalizar_texto(nome_aba)

    mes_encontrado = None
    for mes_nome, mes_num in MESES_PT.items():
        if mes_nome in nome:
            mes_encontrado = mes_num
            break

    ano_match = re.search(r"\b(20\d{2})\b", nome)
    ano_encontrado = int(ano_match.group(1)) if ano_match else None

    return mes_encontrado, ano_encontrado


def label_mes_ano(mes: int, ano: int) -> str:
    return f"{MESES_PT_REV[mes]} {ano}"


def eh_x(valor) -> bool:
    if valor is None:
        return False
    texto = normalizar_texto(valor)
    return texto == "x"


def buscar_cidades(termo: str, lista_cidades: list[str]) -> list[str]:
    termo = normalizar_texto(termo)

    if not termo:
        return lista_cidades[:100]

    resultados = [
        cidade for cidade in lista_cidades
        if termo in normalizar_texto(cidade)
    ]

    return resultados[:100]


def parsear_data_coluna(coluna):
    if coluna is None:
        return None

    texto = str(coluna).strip()
    match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    if not match:
        return None

    try:
        return datetime.strptime(match.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


@st.cache_resource
def conectar_drive():
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]

    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes
    )

    service = build("drive", "v3", credentials=creds)
    return service


@st.cache_data(show_spinner=False, ttl=3600)
def baixar_excel_drive(id_arquivo: str) -> bytes:
    service = conectar_drive()
    request = service.files().get_media(fileId=id_arquivo)

    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    concluido = False
    while not concluido:
        _, concluido = downloader.next_chunk()

    return buffer.getvalue()


@st.cache_data(show_spinner=False, ttl=3600)
def carregar_abas_drive(id_arquivo: str):
    excel_bytes = baixar_excel_drive(id_arquivo)
    excel = pd.ExcelFile(io.BytesIO(excel_bytes))

    abas_validas = []

    for aba in excel.sheet_names:
        estado = estado_da_aba(aba)
        mes, ano = extrair_mes_ano_da_aba(aba)

        if estado and mes and ano:
            abas_validas.append({
                "sheet_name": aba,
                "estado": estado,
                "mes": mes,
                "ano": ano,
                "label": label_mes_ano(mes, ano),
                "ordem": ano * 100 + mes
            })

    abas_validas = sorted(abas_validas, key=lambda x: x["ordem"])
    return abas_validas


@st.cache_data(show_spinner=False, ttl=3600)
def ler_aba_drive(id_arquivo: str, nome_aba: str) -> pd.DataFrame:
    excel_bytes = baixar_excel_drive(id_arquivo)

    bruto = pd.read_excel(
        io.BytesIO(excel_bytes),
        sheet_name=nome_aba,
        header=None
    )

    bruto = bruto.dropna(axis=1, how="all")

    linha_datas = bruto.iloc[0]
    linha_cabecalho = bruto.iloc[1]

    colunas = []
    for i in range(len(bruto.columns)):
        valor_cab = linha_cabecalho.iloc[i]
        valor_data = linha_datas.iloc[i]

        if pd.notna(valor_cab) and str(valor_cab).strip():
            colunas.append(str(valor_cab).strip())
        elif pd.notna(valor_data) and str(valor_data).strip():
            colunas.append(str(valor_data).strip())
        else:
            colunas.append(f"COL_{i}")

    df = bruto.iloc[2:].copy()
    df.columns = colunas
    df = df.dropna(axis=0, how="all").reset_index(drop=True)

    return df


def obter_coluna_cidade(df: pd.DataFrame):
    for col in df.columns:
        if normalizar_texto(col) == "cidade":
            return col
    return None


def dia_semana_pt(data_obj: date) -> str:
    nomes = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo",
    }
    return nomes[data_obj.weekday()]


def preparar_cidades(df: pd.DataFrame, coluna_cidade: str) -> list[str]:
    cidades = (
        df[coluna_cidade]
        .dropna()
        .astype(str)
        .str.strip()
    )

    cidades = [c for c in cidades.tolist() if c.strip()]
    cidades = sorted(set(cidades), key=lambda x: normalizar_texto(x))
    return cidades


def encontrar_linha_cidade(df: pd.DataFrame, coluna_cidade: str, cidade_escolhida: str):
    alvo = normalizar_texto(cidade_escolhida)

    for _, row in df.iterrows():
        cidade = row.get(coluna_cidade)
        if normalizar_texto(cidade) == alvo:
            return row

    return None


def obter_dias_coleta(row: pd.Series, mes: int, ano: int) -> list[date]:
    dias = []

    for coluna in row.index:
        data_col = parsear_data_coluna(coluna)
        if not data_col:
            continue

        if data_col.month == mes and data_col.year == ano and eh_x(row[coluna]):
            if data_col.weekday() < 5:
                dias.append(data_col)

    dias = sorted(set(dias))
    return dias


def html_calendario(mes: int, ano: int, dias_destacados: list[int]) -> str:
    cal = calendar.Calendar(firstweekday=6)
    semanas = cal.monthdayscalendar(ano, mes)
    hoje = datetime.now().date()

    nomes_dias = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]

    html = """
    <style>
        .calendar-wrapper {
            width: 100%;
            max-width: 680px;
            margin-top: 8px;
            font-family: Arial, sans-serif;
        }
        .calendar-title {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 14px;
            color: #1F2937;
        }
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
        }
        .calendar-header {
            background: #EAF2FF;
            color: #0B3C91;
            text-align: center;
            padding: 10px 4px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 12px;
            border: 1px solid #D6E4FF;
        }
        .calendar-day {
            min-height: 62px;
            border-radius: 14px;
            padding: 8px 10px;
            border: 2px solid #D1D5DB;
            background: #FFFFFF;
            display: flex;
            align-items: flex-start;
            justify-content: flex-end;
            font-size: 16px;
            font-weight: 700;
            color: #111827;
            box-sizing: border-box;
            transition: all 0.15s ease;
        }
        .calendar-weekend {
            background: #E5E7EB !important;
            color: #6B7280 !important;
            border: 2px solid #6B7280 !important;
        }
        .calendar-highlight {
            background: #10B981 !important;
            color: white !important;
            border: 2px solid #059669 !important;
            box-shadow: 0 6px 18px rgba(16, 185, 129, 0.25);
        }
        .calendar-today {
            border: 3px solid #1A73E8 !important;
            box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.15);
            position: relative;
        }

        .calendar-today::after {
            content: "";
            position: absolute;
            top: 6px;
            left: 6px;
            width: 6px;
            height: 6px;
            background: #1A73E8;
            border-radius: 50%;
        }
        .calendar-skip {
            min-height: 62px;
            background: transparent;
            border: none;
        }
    </style>
    """

    html += '<div class="calendar-wrapper">'
    html += f'<div class="calendar-title">{MESES_PT_REV[mes]} {ano}</div>'
    html += '<div class="calendar-grid">'

    for nome_dia in nomes_dias:
        html += f'<div class="calendar-header">{nome_dia}</div>'

    for semana in semanas:
        for j, dia in enumerate(semana):
            if dia == 0:
                html += '<div class="calendar-skip"></div>'
            else:
                classes = ["calendar-day"]

                if j in [0, 6]:
                    classes.append("calendar-weekend")

                if dia in dias_destacados:
                    classes.append("calendar-highlight")

                if date(ano, mes, dia) == hoje:
                    classes.append("calendar-today")

                html += f'<div class="{" ".join(classes)}">{dia}</div>'

    html += "</div></div>"
    return html


def sugerir_mes_padrao(opcoes_mes: list[dict]) -> int:
    hoje = datetime.now()
    ordem_hoje = hoje.year * 100 + hoje.month

    for i, item in enumerate(opcoes_mes):
        if item["ordem"] == ordem_hoje:
            return i

    return len(opcoes_mes) - 1 if opcoes_mes else 0


def altura_calendario(mes: int, ano: int) -> int:
    cal = calendar.Calendar(firstweekday=6)
    semanas = cal.monthdayscalendar(ano, mes)

    if len(semanas) <= 5:
        return 470
    return 560


# =========================================================
# ENTRADA DO ARQUIVO
# =========================================================
try:
    abas_validas = carregar_abas_drive(ID_ARQUIVO_DRIVE)
except KeyError:
    st.error("Credenciais não encontradas no secrets.toml. Verifique a chave 'gcp_service_account'.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao abrir a planilha: {repr(e)}")
    st.code(traceback.format_exc())
    st.stop()

if not abas_validas:
    st.error("Nenhuma aba válida de calendário foi encontrada no arquivo.")
    st.stop()


# =========================================================
# FILTROS PRINCIPAIS
# =========================================================
st.markdown("""
<div class="section-card">
    <div class="section-title">Selecione os filtros abaixo para consultar as datas das coletas em sua cidade.</div>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

with col_f1:
    estado = st.radio(
        "Estado",
        options=["SP", "MG"],
        horizontal=True
    )

opcoes_estado = [aba for aba in abas_validas if aba["estado"] == estado]

if not opcoes_estado:
    st.warning(f"Não encontrei abas para o estado {estado}.")
    st.stop()

indice_padrao_mes = sugerir_mes_padrao(opcoes_estado)

with col_f2:
    labels_meses = [item["label"] for item in opcoes_estado]
    mes_escolhido_label = st.selectbox(
        "Mês",
        options=labels_meses,
        index=indice_padrao_mes
    )

aba_escolhida = next(item for item in opcoes_estado if item["label"] == mes_escolhido_label)

try:
    df = ler_aba_drive(ID_ARQUIVO_DRIVE, aba_escolhida["sheet_name"])
except Exception as e:
    st.error(f"Erro ao ler a aba '{aba_escolhida['sheet_name']}': {e}")
    st.stop()

coluna_cidade = obter_coluna_cidade(df)
if not coluna_cidade:
    st.error("Não encontrei a coluna 'CIDADE' na aba selecionada.")
    st.stop()

cidades = preparar_cidades(df, coluna_cidade)

with col_f3:
    cidade_escolhida = st_searchbox(
        lambda termo: buscar_cidades(termo, cidades),
        label="Cidade",
        placeholder="Digite o nome da cidade...",
        key="cidade_searchbox"
    )


# =========================================================
# RESULTADO
# =========================================================
if cidade_escolhida:
    row = encontrar_linha_cidade(df, coluna_cidade, cidade_escolhida)

    if row is None:
        st.error("Não foi possível localizar a linha da cidade na planilha.")
        st.stop()

    dias_datas = obter_dias_coleta(
        row=row,
        mes=aba_escolhida["mes"],
        ano=aba_escolhida["ano"]
    )

    dias_numeros = [d.day for d in dias_datas]

    st.markdown("---")
    st.markdown(
        f"""
        <div class="result-title">📍 {cidade_escolhida} - {estado}</div>
        """,
        unsafe_allow_html=True
    )

    col_cal, col_lista = st.columns([1.35, 1])

    with col_cal:
        calendario_html = html_calendario(
            mes=aba_escolhida["mes"],
            ano=aba_escolhida["ano"],
            dias_destacados=dias_numeros
        )

        altura_html = altura_calendario(
            aba_escolhida["mes"],
            aba_escolhida["ano"]
        )

        st.components.v1.html(
            calendario_html,
            height=altura_html,
            scrolling=False
        )

    with col_lista:
        if dias_datas:

            hoje = datetime.now().date()

            tem_coleta_hoje = hoje in dias_datas

            # Encontrar próxima coleta futura (>= hoje)
            proximas_futuras = [d for d in dias_datas if d >= hoje]

            proxima = proximas_futuras[0] if proximas_futuras else None

            if tem_coleta_hoje:
                texto = "📅 Hoje: Tem coleta"
            else:
                if proxima:
                    texto = f"""📅 Hoje: Sem coleta<br>
        Próxima coleta: {proxima.strftime('%d/%m')} ({dia_semana_pt(proxima)})"""
                else:
                    texto = "📅 Hoje: Sem coleta<br>⏭ Próxima coleta: -"

            st.markdown(f"""
            <div class="section-card" style="padding: 16px 18px; margin-bottom: 22px;">
                <div style="font-size: 1.05rem; font-weight: 600; color: #1F2937;">
                    {texto}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Lista completa
            st.markdown("### 📋 Lista completa")

            texto_copiavel = "\n".join(
                f"{d.strftime('%d/%m')} - {dia_semana_pt(d)}"
                for d in dias_datas
            )

            st.code(texto_copiavel, language=None)

        else:
            st.warning("Não há coletas marcadas para essa cidade neste mês.")


# =========================================================
# RODAPÉ
# =========================================================
st.markdown("---")
st.markdown(
    """
    <div class="footer-note">
        Base atualizada automaticamente a cada 60 minutos
    </div>
    """,
    unsafe_allow_html=True
)