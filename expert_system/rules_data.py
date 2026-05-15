from .engine import Rule

# Datos de las preferencias (HECHOS iniciales)
PREFERENCIAS_TURISMO = [
    {"id": "playa", "label": "Gusto por la Playa", "desc": "Preferencia por destinos costeros y arena."},
    {"id": "montana", "label": "Gusto por la Montaña", "desc": "Preferencia por elevaciones y aire puro."},
    {"id": "clima_calido", "label": "Prefiere Clima Cálido", "desc": "Temperaturas altas y sol."},
    {"id": "clima_frio", "label": "Prefiere Clima Frío", "desc": "Temperaturas bajas o nieve."},
    {"id": "presupuesto_alto", "label": "Presupuesto Alto", "desc": "Disponibilidad para servicios premium."},
    {"id": "deporte", "label": "Le gusta el Deporte", "desc": "Busca actividad física intensa."},
    {"id": "historia", "label": "Interés Histórico", "desc": "Busca aprender sobre el pasado."},
]

# Base de conocimiento (REGLAS)
REGLAS_TURISMO = [
    Rule(
        id="R1",
        name="Perfil Veraniego",
        logic="SI (Gusto Playa) Y (Clima Cálido) ENTONCES Perfil Veraniego",
        conditions=["playa", "clima_calido"],
        conclusions=["perfil_veraniego"],
        explanation="Si te gusta la playa y el sol, el sistema deduce que tienes un perfil veraniego."
    ),
    Rule(
        id="R2",
        name="Perfil Alpino",
        logic="SI (Gusto Montaña) Y (Clima Frío) ENTONCES Perfil Alpino",
        conditions=["montana", "clima_frio"],
        conclusions=["perfil_alpino"],
        explanation="La combinación de montaña y frío permite inferir un perfil alpino."
    ),
    Rule(
        id="R3",
        name="Destino: Caribe Premium",
        logic="SI (Perfil Veraniego) Y (Presupuesto Alto) ENTONCES Destino: Caribe Resort",
        conditions=["perfil_veraniego", "presupuesto_alto"],
        conclusions=["destino_caribe_resort"],
        explanation="Como ya sabemos que eres veraniego y tienes presupuesto, la mejor opción es el Caribe."
    ),
    Rule(
        id="R4",
        name="Destino: Alpes Suizos",
        logic="SI (Perfil Alpino) Y (Le gusta el Deporte) ENTONCES Destino: Esquí en Alpes",
        conditions=["perfil_alpino", "deporte"],
        conclusions=["destino_esqui_alpes"],
        explanation="Un perfil alpino deportista activa la regla para recomendar esquí en los Alpes."
    ),
    Rule(
        id="R5",
        name="Destino: Cusco Histórico",
        logic="SI (Gusto Montaña) Y (Interés Histórico) ENTONCES Destino: Cusco / Machu Picchu",
        conditions=["montana", "historia"],
        conclusions=["destino_cusco_historico"],
        explanation="La montaña con historia dispara la regla hacia un destino arqueológico como Cusco."
    ),
    Rule(
        id="R6",
        name="Perfil Aventurero (General)",
        logic="SI (Gusto Montaña) ENTONCES Perfil Aventurero",
        conditions=["montana"],
        conclusions=["perfil_aventurero"],
        explanation="Cualquier gusto por la montaña implica un perfil aventurero básico.",
        priority=1
    ),
    Rule(
        id="R7",
        name="Perfil Aventurero Extremo (Específico)",
        logic="SI (Gusto Montaña) Y (Le gusta el Deporte) ENTONCES Perfil Aventurero Extremo",
        conditions=["montana", "deporte"],
        conclusions=["perfil_aventurero_extremo"],
        explanation="Si además de montaña le gusta el deporte, el perfil es extremo. Esta regla es más específica.",
        priority=1
    )
]
