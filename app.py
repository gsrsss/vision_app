import os
import streamlit as st
import base64
from openai import OpenAI

# --- Función para codificar la imagen a base64 ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# --- Configuración de la página de Streamlit ---
st.set_page_config(page_title="Análisis de Imagen", layout="centered")

# --- Estilos CSS personalizados ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 700px; /* Ancho máximo para el contenido principal */
    }
    h1 {
        text-align: center;
        color: #2c3e50; /* Un color oscuro para el título */
        font-family: 'Arial', sans-serif;
    }
    .stSubheader {
        text-align: center;
        color: #7f8c8d; /* Gris para subtítulos */
        font-style: italic;
        margin-bottom: 1.5rem;
    }
    .section-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px 35px; /* Más padding horizontal */
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 1px solid #ecf0f1; /* Borde más suave */
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #3498db; /* Azul vibrante para el botón */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #2980b9; /* Azul más oscuro al pasar el ratón */
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    /* Estilo para las advertencias, infos y éxitos */
    .stAlert {
        border-radius: 8px;
    }
    .stImage {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stTextArea [data-testid="stExpander"] {
        border-radius: 8px;
        border: 1px solid #ced4da;
    }
    /* Placeholder para el text_input de la API key */
    .stTextInput>div>div>input::placeholder {
        color: #bdc3c7;
    }
    /* Ajustes para el spinner */
    .stSpinner > div > div {
        color: #3498db !important; /* Color del spinner */
    }
    /* Mejorar la legibilidad de la respuesta */
    .st-emotion-cache-nahz7x { /* Targeting the markdown output container */
        background-color: #f8f9fa; /* Fondo ligeramente gris */
        border-left: 5px solid #3498db; /* Borde azul a la izquierda */
        padding: 15px;
        border-radius: 8px;
        line-height: 1.6;
        color: #34495e;
        font-size: 1.05rem;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Análisis de Imagen con IA ദ്ദി๑>؂•̀๑)")
st.subheader("Sube una imagen y deja que la inteligencia artificial de OpenAI la describa por ti.")

ke = None
with st.container():
    st.markdown("### 🔑 Paso 1: Ingresa tu Clave de API de OpenAI")
    ke_input = st.text_input('Tu clave aquí (sk-...):', type="password", label_visibility="collapsed", placeholder="sk-...")
    
    if not ke_input:
        st.info("⚠️ Necesitas una clave de OpenAI para usar esta aplicación.")
    else:
        os.environ['OPENAI_API_KEY'] = ke_input
        ke = ke_input
        st.success("¡Clave de API cargada! . ݁₊ ⊹ . ݁")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Contenedor para la carga de imagen (solo si hay API Key) ---
uploaded_file = None
if ke:
    with st.container():
        st.markdown("### 📸 Paso 2: Sube tu Imagen")
        uploaded_file = st.file_uploader("Elige una imagen", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

        if uploaded_file:
            st.image(uploaded_file, caption="Imagen cargada", use_container_width=True)
        else:
            st.info("Por favor, sube una imagen para empezar el análisis.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Contenedor para la pregunta específica (solo si hay imagen y API Key) ---
additional_details = ""
if uploaded_file and ke:
    with st.container():
        st.markdown("### 💬 Paso 3: Pregunta algo específico (Opcional)")
        show_details = st.toggle("¿Quieres hacer una pregunta concreta sobre la imagen?", value=False)

        if show_details:
            additional_details = st.text_area(
                "Escribe tu pregunta o contexto adicional aquí:",
                placeholder="Por ejemplo: '¿De qué raza es el perro?', '¿Qué emoción expresa la persona?', etc."
            )
        st.markdown('</div>', unsafe_allow_html=True)

# --- Botón de Análisis ---
if uploaded_file and ke:
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2: # Centrar el botón
        analyze_button = st.button("✨ Analizar Imagen", type="secondary", use_container_width=True)
else:
    analyze_button = False # Asegura que el botón no se active si falta algo

# --- Lógica de Análisis ---
if analyze_button and uploaded_file is not None and ke:
    try:
        # Inicializar el cliente de OpenAI
        client = OpenAI(api_key=ke) # Usar la clave ingresada directamente

        with st.spinner("Analizando la imagen, por favor espera... 🧠"):
            base64_image = encode_image(uploaded_file)
            
            prompt_text = "Describe detalladamente lo que ves en esta imagen en español."
            if show_details and additional_details:
                prompt_text = additional_details # Si hay pregunta específica, usa eso como prompt principal

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ]
            
            # Realizar la solicitud a la API de OpenAI
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", # Modelo actualizado
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Actualización final del placeholder después de que el stream termina
            message_placeholder.markdown(full_response)
        
    except Exception as e:
        st.error(f"⚠️ ¡Ha ocurrido un error durante el análisis! Por favor, verifica tu clave de API o intenta con otra imagen. Error: {e}")
