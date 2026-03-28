"""
AgriTrace - Módulo de Agente IA (Prueba de Concepto)
Este script demuestra la arquitectura lógica de un Agente IA (Text-to-SQL).
El agente toma preguntas de negocio en lenguaje natural y genera las consultas 
SQL correspondientes utilizando el contexto de nuestros modelos de Django.
"""

class AgriTraceAIAgent:
    def __init__(self, db_connection="postgresql://localhost:5432/agritrace"):
        self.db = db_connection
        # En producción, aquí se inicializaría LangChain con OpenAI API
        self.llm_model = "gpt-3.5-turbo (Simulado para Portfolio)"
        print(f" Agente IA inicializado con modelo: {self.llm_model}")

    def _generar_prompt_contexto(self, pregunta_usuario):
        """
        Inyecta la estructura de la base de datos (Prompt Engineering) para que 
        el LLM entienda cómo cruzar las tablas de Productores y Predios.
        """
        esquema_bd = """
        Tablas disponibles:
        - modulo_a_productor (id, numero_documento, nombres, apellidos)
        - modulo_a_predio (id, productor_id, departamento, eudr_compliant, hectareas)
        - modulo_b_plancampana (id, predio_id, estatus_general, uso_insumos_prohibidos)
        """
        
        prompt = f"""
        Eres un agente experto en SQL. Tienes acceso al siguiente esquema:
        {esquema_bd}
        
        Pregunta del usuario de negocio: "{pregunta_usuario}"
        Genera la consulta SQL exacta para responder a esta métrica.
        """
        return prompt

    def ejecutar_consulta_ia(self, pregunta_usuario):
        print(f"\n Mánager de Planta pregunta: '{pregunta_usuario}'")
        print(" Agente procesando el contexto relacional...")
        
        prompt = self._generar_prompt_contexto(pregunta_usuario)
        
        # Simulación de la respuesta del LLM (agente) mapeando a la query EUDR
        if "Europa" in pregunta_usuario or "EUDR" in pregunta_usuario:
            sql_generado = """
            SELECT departamento, COUNT(DISTINCT p.id) AS total_productores, 
                   SUM(pa.hectareas) AS total_hectareas_certificadas
            FROM modulo_a_productor p
            JOIN modulo_a_predio pr ON p.id = pr.productor_id
            JOIN modulo_b_parcela pa ON pr.id_predio = pa.predio_id
            WHERE pr.eudr_compliant = TRUE
            GROUP BY pr.departamento;
            """
        else:
            sql_generado = " Consulta SQL generada dinámicamente..."

        print(f" SQL Generado por el Agente:\n{sql_generado}")
        return sql_generado

# ==========================================
# EJECUCIÓN DEL AGENTE
# ==========================================
if __name__ == "__main__":
    agente = AgriTraceAIAgent()
    
    # Simulamos una consulta real de la gerencia
    pregunta = "¿Cuántas hectáreas tenemos listas y certificadas para exportar a Europa por departamento?"
    
    query_resultante = agente.ejecutar_consulta_ia(pregunta)
